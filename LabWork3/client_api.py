"""
GSD Meter API Client
Клиент для взаимодействия с API оценки GSD аэрофотоснимков
"""

import requests
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class QualityGrade(Enum):
    """Оценки качества изображения"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class ImageStatus(Enum):
    """Статусы обработки изображения"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ImageInfo:
    """Информация об изображении из БД"""
    id: int
    filename: str
    upload_date: str
    file_size: int
    width: int
    height: int
    format: str
    status: str


@dataclass
class QualityMetrics:
    """Метрики качества изображения"""
    id: int
    sharpness_score: float
    noise_level: float
    contrast_ratio: float
    blur_detected: bool
    quality_grade: str


@dataclass
class ModelInfo:
    """Информация о модели нейронной сети"""
    id: int
    model_name: str
    version: str
    architecture: str


@dataclass
class GSDAssessment:
    """Результат оценки GSD"""
    id: int
    image_id: int
    model_id: int
    gsd_value: float
    confidence_score: float
    processing_time: float
    assessment_date: str
    metadata: Optional[dict] = None


@dataclass
class AssessmentResult:
    """Полный результат оценки с вложенными данными"""
    assessment: GSDAssessment
    image: ImageInfo
    model: ModelInfo
    quality_metrics: QualityMetrics


class GSDClientException(Exception):
    """Базовое исключение клиента"""
    pass


class APIError(GSDClientException):
    """Ошибка API сервера"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class ValidationError(GSDClientException):
    """Ошибка валидации данных"""
    pass


class HTTPClient:
    """
    Низкоуровневый HTTP клиент для работы с API.
    Отвечает только за выполнение HTTP запросов.
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Args:
            base_url: Базовый URL API сервера
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GSD-Client/1.0',
            'Accept': 'application/json'
        })
    
    def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Выполнение HTTP запроса
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Endpoint API
            **kwargs: Дополнительные параметры для requests
            
        Returns:
            Распарсенный JSON ответ
            
        Raises:
            APIError: При ошибках API
            GSDClientException: При проблемах с соединением
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code >= 400:
                error_message = self._extract_error_message(response)
                raise APIError(response.status_code, error_message)
            
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise GSDClientException(f"Не удалось подключиться к серверу: {self.base_url}")
        except requests.exceptions.Timeout:
            raise GSDClientException(f"Превышено время ожидания ({self.timeout}s)")
        except requests.exceptions.RequestException as e:
            raise GSDClientException(f"Ошибка запроса: {str(e)}")
        except APIError:
            raise
        except Exception as e:
            raise GSDClientException(f"Непредвиденная ошибка: {str(e)}")
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """
        Извлечение сообщения об ошибке из ответа
        
        Args:
            response: Объект ответа requests
            
        Returns:
            Сообщение об ошибке
        """
        try:
            data = response.json()
            return data.get('detail', data.get('error', response.text))
        except:
            return response.text or "Unknown error"
    
    def close(self):
        """Закрытие HTTP сессии"""
        self.session.close()


class FileValidator:
    """
    Валидатор файлов изображений.
    Отвечает только за проверку файлов перед отправкой.
    """
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    @classmethod
    def validate_path(cls, file_path: str) -> Path:
        """
        Валидация пути к файлу
        
        Args:
            file_path: Путь к файлу изображения
            
        Returns:
            Объект Path
            
        Raises:
            ValidationError: При ошибках валидации
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"Файл не найден: {file_path}")
        
        if not path.is_file():
            raise ValidationError(f"Путь не является файлом: {file_path}")
        
        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Неподдерживаемый формат файла: {path.suffix}. "
                f"Поддерживаемые: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        
        file_size = path.stat().st_size
        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"Файл слишком большой: {file_size / 1024 / 1024:.1f} MB. "
                f"Максимум: {cls.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
            )
        
        return path
    
    @classmethod
    def validate_bytes(cls, data: bytes, filename: str = "image.jpg"):
        """
        Валидация байтовых данных
        
        Args:
            data: Байты изображения
            filename: Имя файла
            
        Raises:
            ValidationError: При ошибках валидации
        """
        if not data:
            raise ValidationError("Пустые данные изображения")
        
        if len(data) > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"Данные слишком большие: {len(data) / 1024 / 1024:.1f} MB"
            )


class ResponseParser:
    """
    Парсер ответов API.
    Отвечает только за преобразование JSON в объекты данных.
    """
    
    @staticmethod
    def parse_assessment_result(data: dict) -> AssessmentResult:
        """
        Парсинг полного результата оценки
        
        Args:
            data: JSON данные от API
            
        Returns:
            Объект AssessmentResult
        """
        assessment = GSDAssessment(
            id=data['assessment']['id'],
            image_id=data['assessment']['image_id'],
            model_id=data['assessment']['model_id'],
            gsd_value=data['assessment']['gsd_value'],
            confidence_score=data['assessment']['confidence_score'],
            processing_time=data['assessment']['processing_time'],
            assessment_date=data['assessment']['assessment_date'],
            metadata=data['assessment'].get('metadata')
        )
        
        image = ImageInfo(
            id=data['image']['id'],
            filename=data['image']['filename'],
            upload_date=data['image']['upload_date'],
            file_size=data['image']['file_size'],
            width=data['image']['width'],
            height=data['image']['height'],
            format=data['image']['format'],
            status=data['image']['status']
        )
        
        model = ModelInfo(
            id=data['model']['id'],
            model_name=data['model']['model_name'],
            version=data['model']['version'],
            architecture=data['model']['architecture']
        )
        
        quality = QualityMetrics(
            id=data['quality_metrics']['id'],
            sharpness_score=data['quality_metrics']['sharpness_score'],
            noise_level=data['quality_metrics']['noise_level'],
            contrast_ratio=data['quality_metrics']['contrast_ratio'],
            blur_detected=data['quality_metrics']['blur_detected'],
            quality_grade=data['quality_metrics']['quality_grade']
        )
        
        return AssessmentResult(
            assessment=assessment,
            image=image,
            model=model,
            quality_metrics=quality
        )
    
    @staticmethod
    def parse_assessment_list(data: List[dict]) -> List[AssessmentResult]:
        """
        Парсинг списка оценок
        
        Args:
            data: Список JSON объектов
            
        Returns:
            Список объектов AssessmentResult
        """
        return [ResponseParser.parse_assessment_result(item) for item in data]
    
    @staticmethod
    def parse_image_info(data: dict) -> ImageInfo:
        """
        Парсинг информации об изображении
        
        Args:
            data: JSON данные
            
        Returns:
            Объект ImageInfo
        """
        return ImageInfo(
            id=data['id'],
            filename=data['filename'],
            upload_date=data['upload_date'],
            file_size=data['file_size'],
            width=data['width'],
            height=data['height'],
            format=data['format'],
            status=data['status']
        )


class GSDAPIClient:
    """
    Высокоуровневый клиент для работы с GSD Assessment API.
    Предоставляет удобный интерфейс для всех операций с API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Args:
            base_url: Базовый URL API сервера
            timeout: Таймаут запросов в секундах
        """
        self._http_client = HTTPClient(base_url, timeout)
        self._validator = FileValidator()
        self._parser = ResponseParser()
    
    def check_health(self) -> bool:
        """
        Проверка доступности API сервиса
        
        Returns:
            True если сервис работает корректно
        """
        try:
            data = self._http_client.request('GET', '/api/v1/health')
            return data.get('status') == 'healthy'
        except:
            return False
    
    def assess_image(self, image_path: str, user_id: Optional[int] = None) -> AssessmentResult:
        """
        Отправка изображения на оценку GSD
        
        Args:
            image_path: Путь к файлу изображения
            user_id: ID пользователя (опционально)
            
        Returns:
            Полный результат оценки
            
        Raises:
            ValidationError: При ошибках валидации файла
            APIError: При ошибках API
            GSDClientException: При других ошибках
        """
        path = self._validator.validate_path(image_path)
        
        with open(path, 'rb') as f:
            return self._send_image(f.read(), path.name, user_id)
    
    def assess_image_from_bytes(
        self, 
        image_bytes: bytes, 
        filename: str = "image.jpg",
        user_id: Optional[int] = None
    ) -> AssessmentResult:
        """
        Отправка изображения из байтов на оценку GSD
        
        Args:
            image_bytes: Байты изображения
            filename: Имя файла для идентификации
            user_id: ID пользователя (опционально)
            
        Returns:
            Полный результат оценки
            
        Raises:
            ValidationError: При ошибках валидации
            APIError: При ошибках API
        """
        self._validator.validate_bytes(image_bytes, filename)
        return self._send_image(image_bytes, filename, user_id)
    
    def _send_image(self, image_data: bytes, filename: str, user_id: Optional[int]) -> AssessmentResult:
        """
        Внутренний метод отправки изображения
        
        Args:
            image_data: Байты изображения
            filename: Имя файла
            user_id: ID пользователя
            
        Returns:
            Результат оценки
        """
        files = {'file': (filename, image_data, 'image/jpeg')}
        params = {}
        if user_id is not None:
            params['user_id'] = user_id
        
        data = self._http_client.request('POST', '/api/v1/assess', files=files, params=params)
        return self._parser.parse_assessment_result(data)
    
    def get_assessment(self, assessment_id: int) -> AssessmentResult:
        """
        Получение результата оценки по ID
        
        Args:
            assessment_id: ID оценки
            
        Returns:
            Результат оценки
            
        Raises:
            APIError: При ошибках API (например, 404 если не найдено)
        """
        data = self._http_client.request('GET', f'/api/v1/assessments/{assessment_id}')
        return self._parser.parse_assessment_result(data)
    
    def get_user_assessments(self, user_id: int, limit: int = 10) -> List[AssessmentResult]:
        """
        Получение списка оценок пользователя
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список результатов оценок
        """
        params = {'limit': limit}
        data = self._http_client.request('GET', f'/api/v1/users/{user_id}/assessments', params=params)
        return self._parser.parse_assessment_list(data)
    
    def get_image_info(self, image_id: int) -> ImageInfo:
        """
        Получение информации об изображении
        
        Args:
            image_id: ID изображения
            
        Returns:
            Информация об изображении
        """
        data = self._http_client.request('GET', f'/api/v1/images/{image_id}')
        return self._parser.parse_image_info(data)
    
    def delete_assessment(self, assessment_id: int) -> bool:
        """
        Удаление оценки
        
        Args:
            assessment_id: ID оценки
            
        Returns:
            True если удаление успешно
        """
        self._http_client.request('DELETE', f'/api/v1/assessments/{assessment_id}')
        return True
    
    def close(self):
        """Закрытие клиента и освобождение ресурсов"""
        self._http_client.close()
    
    def __enter__(self):
        """Поддержка context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка context manager"""
        self.close()


def format_result(result: AssessmentResult) -> str:
    """
    Форматирование результата оценки в читаемую строку
    
    Args:
        result: Результат оценки
        
    Returns:
        Отформатированная строка
    """
    lines = [
        "=" * 70,
        "РЕЗУЛЬТАТЫ ОЦЕНКИ GSD",
        "=" * 70,
        f"ID оценки:        {result.assessment.id}",
        f"GSD:              {result.assessment.gsd_value} см/пиксель",
        f"Уверенность:      {result.assessment.confidence_score:.2%}",
        f"Время обработки:  {result.assessment.processing_time:.3f} сек",
        f"",
        "Изображение:",
        f"  ID:             {result.image.id}",
        f"  Файл:           {result.image.filename}",
        f"  Размер:         {result.image.width}x{result.image.height} px",
        f"  Формат:         {result.image.format}",
        f"  Размер файла:   {result.image.file_size / 1024:.1f} KB",
        f"  Статус:         {result.image.status}",
        f"",
        "Модель:",
        f"  Название:       {result.model.model_name}",
        f"  Версия:         {result.model.version}",
        f"  Архитектура:    {result.model.architecture}",
        f"",
        "Метрики качества:",
        f"  Резкость:       {result.quality_metrics.sharpness_score:.2f}",
        f"  Шум:            {result.quality_metrics.noise_level:.2f}",
        f"  Контраст:       {result.quality_metrics.contrast_ratio:.2f}",
        f"  Размытие:       {'Обнаружено' if result.quality_metrics.blur_detected else 'Не обнаружено'}",
        f"  Оценка:         {result.quality_metrics.quality_grade}",
        "=" * 70,
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    with GSDAPIClient(base_url="http://localhost:8000") as client:
        if not client.check_health():
            print("Сервис недоступен")
            exit(1)
        
        try:
            result = client.assess_image("aerial_photo.jpg", user_id=1)
            print(format_result(result))
            
        except ValidationError as e:
            print(f"Ошибка валидации: {e}")
        except APIError as e:
            print(f"Ошибка API: {e}")
        except GSDClientException as e:
            print(f"Ошибка клиента: {e}")