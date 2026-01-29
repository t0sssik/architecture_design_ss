# Документация API GSD Assessment Service

## Базовый URL

`http://localhost:8000/api/v1`

## Пользователи (Users)

**Общие поля:**

- id (integer) — внутренний ID пользователя.
- username (string) — уникальное имя пользователя.
- email (string) — email пользователя (валидный формат).
- role (string) — роль пользователя. Возможные значения: "user", "admin", "moderator".
- registration_date (string, datetime) — дата и время регистрации.
- api_key (string) — уникальный API ключ пользователя.

### GET /users

Описание: Получить список всех пользователей.

Query параметры: не требуются

Ответ 200 (application/json):

```json
[
  {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "registration_date": "2023-10-15T14:30:00.123456",
    "api_key": "550e8400-e29b-41d4"
  }
]
```

### GET /users/{user_id}

Описание: Получить информацию о конкретном пользователе.

Path параметры:

- user_id (integer) — ID пользователя.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "user",
  "registration_date": "2023-10-15T14:30:00.123456",
  "api_key": "550e8400-e29b-41d4"
}
```

Ошибки:

- 404 Not Found — если пользователь не найден.

### POST /users

Описание: Создать нового пользователя.

Request body (application/json):

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "role": "user"
}
```

Ответ 201 (application/json):

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "role": "user",
  "registration_date": "2023-10-15T14:30:00.123456",
  "api_key": "550e8400-e29b-41d4"
}
```

Ошибки:

- 400 Bad Request — если email или username уже зарегистрированы.

### PUT /users/{user_id}

Описание: Обновить информацию о пользователе.

Path параметры:

- user_id (integer) — ID пользователя.

Request body (application/json):

```json
{
  "username": "updated_user",
  "email": "updated@example.com",
  "role": "admin"
}
```

Все поля опциональны.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "username": "updated_user",
  "email": "updated@example.com",
  "role": "admin",
  "registration_date": "2023-10-15T14:30:00.123456",
  "api_key": "550e8400-e29b-41d4"
}
```

Ошибки:

- 404 Not Found — если пользователь не найден.

### DELETE /users/{user_id}

Описание: Удалить пользователя.

Path параметры:

- user_id (integer) — ID пользователя.

Ответ 200 (application/json):

```json
{
  "message": "User 'testuser' deleted successfully"
}
```

Ошибки:

- 404 Not Found — если пользователь не найден.

## Изображения (Images)

Общие поля:

- id (integer) — внутренний ID изображения.

- user_id (integer) — ID пользователя, загрузившего изображение.

- filename (string) — имя файла изображения.

- upload_date (string, datetime) — дата и время загрузки.

- file_size (integer) — размер файла в байтах.

- width (integer) — ширина изображения в пикселях.

- height (integer) — высота изображения в пикселях.

- format (string) — формат изображения (jpg, png, etc.).

- status (string) — статус обработки. Возможные значения: "uploaded", "processing", "completed", "failed".

### GET /images

Описание: Получить список всех изображений.

Query параметры: не требуются

Ответ 200 (application/json):

```json
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "test_image.jpg",
    "upload_date": "2023-10-15T15:45:00.123456",
    "file_size": 2048000,
    "width": 1920,
    "height": 1080,
    "format": "jpg",
    "status": "uploaded"
  }
]
```

### GET /images/{image_id}

Описание: Получить информацию о конкретном изображении.

Path параметры:

- image_id (integer) — ID изображения.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "user_id": 1,
  "filename": "test_image.jpg",
  "upload_date": "2023-10-15T15:45:00.123456",
  "file_size": 2048000,
  "width": 1920,
  "height": 1080,
  "format": "jpg",
  "status": "uploaded"
}
```

Ошибки:

- 404 Not Found — если изображение не найдено.

### POST /images

Описание: Загрузить новое изображение.

Request body (application/json):

```json
{
  "user_id": 1,
  "filename": "test_image.jpg",
  "file_size": 2048000,
  "width": 1920,
  "height": 1080,
  "format": "jpg"
}
```

Ответ 201 (application/json):

```json
{
  "id": 1,
  "user_id": 1,
  "filename": "test_image.jpg",
  "upload_date": "2023-10-15T15:45:00.123456",
  "file_size": 2048000,
  "width": 1920,
  "height": 1080,
  "format": "jpg",
  "status": "uploaded"
}
```

Ошибки:

- 404 Not Found — если пользователь не найден.

### PUT /images/{image_id}

Описание: Обновить метаданные изображения.

Path параметры:

- image_id (integer) — ID изображения.

Request body (application/json):

```json
{
  "filename": "updated_image.jpg",
  "status": "completed"
}
```

Все поля опциональны.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "user_id": 1,
  "filename": "updated_image.jpg",
  "upload_date": "2023-10-15T15:45:00.123456",
  "file_size": 2048000,
  "width": 1920,
  "height": 1080,
  "format": "jpg",
  "status": "completed"
}
```

Ошибки:

- 404 Not Found — если изображение не найдено.

### DELETE /images/{image_id}

Описание: Удалить изображение.

Path параметры:

- image_id (integer) — ID изображения.

Ответ 200 (application/json):

```json
{
  "message": "Image 'test_image.jpg' deleted successfully"
}
```

Ошибки:

- 404 Not Found — если изображение не найдено.

## Нейросетевые модели (Neural Network Models)

Общие поля:

- id (integer) — внутренний ID модели.

- model_name (string) — название модели.

- version (string) — версия модели.

- architecture (string) — архитектура нейросети.

- training_date (string, datetime) — дата обучения модели.

- accuracy (float) — точность модели (0.0 - 1.0).

- is_active (boolean) — активна ли модель.

- parameters (object) — параметры модели (JSON).

### GET /models

Описание: Получить список всех моделей.

Query параметры: Не требуются

Ответ 200 (application/json):

```json
[
  {
    "id": 1,
    "model_name": "gsd-detector-v1",
    "version": "1.0.0",
    "architecture": "ResNet50",
    "training_date": "2023-10-10T10:00:00.123456",
    "accuracy": 0.95,
    "is_active": true,
    "parameters": {
      "learning_rate": 0.001,
      "batch_size": 32
    }
  }
]
```

### GET /models/{model_id}

Описание: Получить информацию о конкретной модели.

Path параметры:

- model_id (integer) — ID модели.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "model_name": "gsd-detector-v1",
  "version": "1.0.0",
  "architecture": "ResNet50",
  "training_date": "2023-10-10T10:00:00.123456",
  "accuracy": 0.95,
  "is_active": true,
  "parameters": {
    "learning_rate": 0.001,
    "batch_size": 32
  }
}
```

Ошибки:

- 404 Not Found — если модель не найдена.

### POST /models

Описание: Зарегистрировать новую модель.

Request body (application/json):

```json
{
  "model_name": "gsd-detector-v1",
  "version": "1.0.0",
  "architecture": "ResNet50",
  "accuracy": 0.95,
  "is_active": true
}
```

Ответ 201 (application/json):

```json
{
  "id": 1,
  "model_name": "gsd-detector-v1",
  "version": "1.0.0",
  "architecture": "ResNet50",
  "training_date": "2023-10-15T16:00:00.123456",
  "accuracy": 0.95,
  "is_active": true,
  "parameters": {}
}
```

### PUT /models/{model_id}

Описание: Обновить информацию о модели.

Path параметры:

- model_id (integer) — ID модели.

Request body (application/json):

```json
{
  "model_name": "updated-model",
  "is_active": false
}
```

Все поля опциональны.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "model_name": "updated-model",
  "version": "1.0.0",
  "architecture": "ResNet50",
  "training_date": "2023-10-10T10:00:00.123456",
  "accuracy": 0.95,
  "is_active": false,
  "parameters": {
    "learning_rate": 0.001,
    "batch_size": 32
  }
}
```

Ошибки:

- 404 Not Found — если модель не найдена.

### DELETE /models/{model_id}

Описание: Удалить модель.

Path параметры:

- model_id (integer) — ID модели.

Ответ 200 (application/json):

```json
{
  "message": "Model 'gsd-detector-v1' deleted successfully"
}
```

Ошибки:

- 404 Not Found — если модель не найдена.

## Оценки GSD (GSD Assessments)

Общие поля:

- id (integer) — внутренний ID оценки.

- image_id (integer) — ID изображения.
  
- model_id (integer) — ID модели, использованной для оценки.
  
- gsd_value (float) — значение GSD (Ground Sample Distance).
  
- confidence_score (float) — уверенность модели (0.0 - 1.0).
  
- processing_time (float) — время обработки в секундах.
  
- assessment_date (string, datetime) — дата и время оценки.
  
- metadata (object) — дополнительные метаданные (JSON).

### GET /assessments

Описание: Получить список всех оценок.

Query параметры: Не требуются

Ответ 200 (application/json):

```json
[
  {
    "id": 1,
    "image_id": 1,
    "model_id": 1,
    "gsd_value": 0.85,
    "confidence_score": 0.92,
    "processing_time": 1.5,
    "assessment_date": "2023-10-15T16:30:00.123456",
    "metadata": {
      "detection_count": 10,
      "average_confidence": 0.9
    }
  }
]
```

### GET /assessments/{assessment_id}

Описание: Получить результаты конкретной оценки.

Path параметры:

- assessment_id (integer) — ID оценки.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "image_id": 1,
  "model_id": 1,
  "gsd_value": 0.85,
  "confidence_score": 0.92,
  "processing_time": 1.5,
  "assessment_date": "2023-10-15T16:30:00.123456",
  "metadata": {
    "detection_count": 10,
    "average_confidence": 0.9
  }
}
```

Ошибки:

- 404 Not Found — если оценка не найдена.

### POST /assessments

Описание: Создать новую оценку GSD.

Request body (application/json):

```json
{
  "image_id": 1,
  "model_id": 1,
  "gsd_value": 0.85,
  "confidence_score": 0.92,
  "processing_time": 1.5
}
```

Ответ 201 (application/json):

```json
{
  "id": 1,
  "image_id": 1,
  "model_id": 1,
  "gsd_value": 0.85,
  "confidence_score": 0.92,
  "processing_time": 1.5,
  "assessment_date": "2023-10-15T16:30:00.123456",
  "metadata": {}
}
```

Ошибки:

- 404 Not Found — если изображение или модель не найдены.

### PUT /assessments/{assessment_id}

Описание: Обновить оценку GSD.

Path параметры:

- assessment_id (integer) — ID оценки.

Request body (application/json):

```json
{
  "gsd_value": 0.9,
  "confidence_score": 0.95
}
```

Все поля опциональны.

Ответ 200 (application/json):

```json
{
  "id": 1,
  "image_id": 1,
  "model_id": 1,
  "gsd_value": 0.9,
  "confidence_score": 0.95,
  "processing_time": 1.5,
  "assessment_date": "2023-10-15T16:30:00.123456",
  "metadata": {
    "detection_count": 10,
    "average_confidence": 0.9
  }
}
```

Ошибки:

- 404 Not Found — если оценка не найдена.

### DELETE /assessments/{assessment_id}

Описание: Удалить оценку GSD.

Path параметры:

- assessment_id (integer) — ID оценки.

Ответ 200 (application/json):

```json
{
  "message": "Assessment for image 1 deleted successfully"
}
```

Ошибки:

- 404 Not Found — если оценка не найдена.

### GET /images/{image_id}/assessments

Описание: Получить все оценки для конкретного изображения.

Path параметры:

- image_id (integer) — ID изображения.

Ответ 200 (application/json):

```json
[
  {
    "id": 1,
    "image_id": 1,
    "model_id": 1,
    "gsd_value": 0.85,
    "confidence_score": 0.92,
    "processing_time": 1.5,
    "assessment_date": "2023-10-15T16:30:00.123456",
    "metadata": {
      "detection_count": 10,
      "average_confidence": 0.9
    }
  }
]
```

Ошибки:

- 404 Not Found — если изображение не найдено.