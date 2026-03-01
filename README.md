# Контрольная работа №1 — FastAPI

## Запуск

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Приложение запустится на http://localhost:8000  
Документация Swagger: http://localhost:8000/docs

## Маршруты

| Метод | URL | Задание | Описание |
|-------|-----|---------|----------|
| GET | / | 1.1 | Приветственное сообщение |
| GET | /html | 1.2 | HTML-страница |
| POST | /calculate?num1=5&num2=10 | 1.3 | Сумма двух чисел |
| GET | /users | 1.4 | Данные пользователя |
| POST | /user | 1.5 | Проверка совершеннолетия |
| POST | /feedback | 2.1 | Сохранение отзыва |
| POST | /feedback/strict | 2.2 | Отзыв с валидацией |

## Примеры запросов

### 1.3 — /calculate
```
POST /calculate?num1=5&num2=10
→ {"result": 15.0}
```

### 1.5 — /user
```json
POST /user
{"name": "Григорий", "age": 20}
→ {"name": "Григорий", "age": 20, "is_adult": true}
```

### 2.1 — /feedback
```json
POST /feedback
{"name": "Rustam", "message": "Отличный день!"}
→ {"message": "Feedback received. Thank you, Rustam."}
```

### 2.2 — /feedback/strict
```json
POST /feedback/strict
{"name": "Артур", "message": "Это тяжело, но я справлюсь!"}
→ {"message": "Спасибо, Артур! Ваш отзыв сохранён."}
```
Запрос с запрещённым словом вернёт HTTP 422.