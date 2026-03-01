from pydantic import BaseModel, Field, field_validator
import re


# Задание 1.4 — модель User с id и name
class User(BaseModel):
    id: int
    name: str


# Задание 1.5 — модель User с age для проверки совершеннолетия
class UserWithAge(BaseModel):
    name: str
    age: int


# Задание 2.1 — модель Feedback (базовая)
class Feedback(BaseModel):
    name: str
    message: str


# Задание 2.2 — модель Feedback с валидацией
BANNED_WORDS = ["кринж", "рофл", "вайб"]

class FeedbackStrict(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def check_banned_words(cls, v: str) -> str:
        v_lower = v.lower()
        for word in BANNED_WORDS:
            # проверяем вхождение слова в любом месте строки
            if re.search(word, v_lower):
                raise ValueError("Использование недопустимых слов")
        return v