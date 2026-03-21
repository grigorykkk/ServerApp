from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class User(BaseModel):
    id: int
    name: str


class UserWithAge(BaseModel):
    name: str
    age: int


class Feedback(BaseModel):
    name: str
    message: str


BANNED_WORDS = ["кринж", "рофл", "вайб"]

class FeedbackStrict(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def check_banned_words(cls, v: str) -> str:
        v_lower = v.lower()
        for word in BANNED_WORDS:
            if re.search(word, v_lower):
                raise ValueError("Использование недопустимых слов")
        return v


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(default=None, gt=0)
    is_subscribed: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Некорректный формат email")
        return value


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., min_length=1)
    accept_language: str = Field(..., min_length=1)

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        pattern = (
            r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?"
            r"(?:,[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?(?:;q=(?:0(?:\.\d+)?|1(?:\.0+)?))?)*$"
        )
        if not re.fullmatch(pattern, value):
            raise ValueError("Некорректный формат Accept-Language")
        return value
