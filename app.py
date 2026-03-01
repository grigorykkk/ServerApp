from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from models import User, UserWithAge, Feedback, FeedbackStrict

# =============================================================
# Задание 1.1 — базовое приложение FastAPI
# Запуск: uvicorn app:app --reload
# =============================================================

app = FastAPI()

# Задание 1.1 — корневой маршрут
@app.get("/")
def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}


# =============================================================
# Задание 1.2 — возврат HTML-страницы
# =============================================================

@app.get("/html", response_class=FileResponse)
def get_html():
    return FileResponse("index.html")


# =============================================================
# Задание 1.3 — POST /calculate, возвращает сумму двух чисел
# =============================================================

@app.post("/calculate")
def calculate(num1: float, num2: float):
    return {"result": num1 + num2}


# =============================================================
# Задание 1.4 — GET /users, возвращает данные пользователя
# =============================================================

current_user = User(id=1, name="Григорий Костин")

@app.get("/users")
def get_user():
    return current_user


# =============================================================
# Задание 1.5 — POST /user, проверяет совершеннолетие
# =============================================================

@app.post("/user")
def check_adult(user: UserWithAge):
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": user.age >= 18,
    }


# =============================================================
# Задание 2.1 — POST /feedback, сохраняет отзыв
# =============================================================

feedbacks_basic: list[dict] = []

@app.post("/feedback")
def receive_feedback(feedback: Feedback):
    feedbacks_basic.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Feedback received. Thank you, {feedback.name}."}


# =============================================================
# Задание 2.2 — POST /feedback/strict, с валидацией и запретом слов
# =============================================================

feedbacks_strict: list[dict] = []

@app.post("/feedback/strict")
def receive_feedback_strict(feedback: FeedbackStrict):
    feedbacks_strict.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}