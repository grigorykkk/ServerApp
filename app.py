from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from models import User, UserWithAge, Feedback, FeedbackStrict


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}



@app.get("/html", response_class=FileResponse)
def get_html():
    return FileResponse("index.html")



@app.post("/calculate")
def calculate(num1: float, num2: float):
    return {"result": num1 + num2}



current_user = User(id=1, name="Григорий Костин")

@app.get("/users")
def get_user():
    return current_user



@app.post("/user")
def check_adult(user: UserWithAge):
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": user.age >= 18,
    }



feedbacks_basic: list[dict] = []

@app.post("/feedback")
def receive_feedback(feedback: Feedback):
    feedbacks_basic.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Feedback received. Thank you, {feedback.name}."}



feedbacks_strict: list[dict] = []

@app.post("/feedback/strict")
def receive_feedback_strict(feedback: FeedbackStrict):
    feedbacks_strict.append({"name": feedback.name, "message": feedback.message})
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}