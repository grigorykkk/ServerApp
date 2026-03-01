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