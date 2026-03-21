from datetime import datetime, timezone
import time
from uuid import UUID, uuid4

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, Signer
from pydantic import ValidationError

from models import (
    CommonHeaders,
    Feedback,
    FeedbackStrict,
    LoginRequest,
    Product,
    User,
    UserCreate,
    UserWithAge,
)


app = FastAPI()

SECRET_KEY = "very-secret-key-for-kr2"
SESSION_COOKIE_NAME = "session_token"
SESSION_TTL_SECONDS = 300
SESSION_REFRESH_THRESHOLD = 180
VALID_USERNAME = "user123"
VALID_PASSWORD = "password123"

signer = Signer(SECRET_KEY, sep=".")

sample_products = [
    Product(product_id=123, name="Smartphone", category="Electronics", price=599.99),
    Product(product_id=456, name="Phone Case", category="Accessories", price=19.99),
    Product(product_id=789, name="Iphone", category="Electronics", price=1299.99),
    Product(product_id=101, name="Headphones", category="Accessories", price=99.99),
    Product(product_id=202, name="Smartwatch", category="Electronics", price=299.99),
]


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


@app.post("/create_user")
def create_user(user: UserCreate):
    return user.model_dump()


@app.get("/products/search")
def search_products(
    keyword: str,
    category: str | None = None,
    limit: int = Query(default=10, ge=1),
):
    normalized_keyword = keyword.lower()
    filtered_products = [
        product
        for product in sample_products
        if normalized_keyword in product.name.lower()
        and (category is None or product.category.lower() == category.lower())
    ]
    return [product.model_dump() for product in filtered_products[:limit]]


@app.get("/product/{product_id}")
def get_product(product_id: int):
    for product in sample_products:
        if product.product_id == product_id:
            return product.model_dump()
    raise HTTPException(status_code=404, detail="Product not found")


def create_session_token(user_id: str, timestamp: int) -> str:
    payload = f"{user_id}.{timestamp}"
    return signer.sign(payload).decode()


def set_session_cookie(response: Response, user_id: str, timestamp: int) -> str:
    token = create_session_token(user_id, timestamp)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        max_age=SESSION_TTL_SECONDS,
    )
    return token


async def parse_login_request(request: Request) -> LoginRequest:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form_data = await request.form()
        payload = dict(form_data)
    return LoginRequest(**payload)


def validate_credentials(credentials: LoginRequest) -> bool:
    return (
        credentials.username == VALID_USERNAME
        and credentials.password == VALID_PASSWORD
    )


def extract_session(session_token: str | None) -> tuple[str, int]:
    if not session_token:
        raise ValueError("missing")

    try:
        unsigned_value = signer.unsign(session_token).decode()
    except BadSignature as exc:
        raise ValueError("invalid") from exc

    parts = unsigned_value.split(".")
    if len(parts) != 2:
        raise ValueError("invalid")

    user_id, timestamp_raw = parts

    try:
        UUID(user_id)
        timestamp = int(timestamp_raw)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid") from exc

    return user_id, timestamp


def require_valid_session(session_token: str | None) -> tuple[str, int]:
    user_id, timestamp = extract_session(session_token)
    now = int(time.time())
    if timestamp > now:
        raise RuntimeError("invalid")
    if now - timestamp > SESSION_TTL_SECONDS:
        raise TimeoutError("expired")
    return user_id, timestamp


@app.post("/login")
async def login(request: Request, response: Response):
    credentials = await parse_login_request(request)
    if not validate_credentials(credentials):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(uuid4())
    issued_at = int(time.time())
    token = set_session_cookie(response, user_id, issued_at)
    return {
        "message": "Login successful",
        "session_token": token,
        "user_id": user_id,
    }


@app.get("/user")
def get_authenticated_user(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    try:
        user_id, timestamp = require_valid_session(session_token)
    except (ValueError, RuntimeError, TimeoutError):
        response.status_code = 401
        return {"message": "Unauthorized"}

    return {
        "user_id": user_id,
        "username": VALID_USERNAME,
        "last_activity": timestamp,
    }


@app.get("/profile")
def get_profile(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    try:
        user_id, timestamp = require_valid_session(session_token)
    except ValueError:
        response.status_code = 401
        return {"message": "Invalid session"}
    except RuntimeError:
        response.status_code = 401
        return {"message": "Invalid session"}
    except TimeoutError:
        response.status_code = 401
        return {"message": "Session expired"}

    now = int(time.time())
    elapsed = now - timestamp

    if SESSION_REFRESH_THRESHOLD <= elapsed < SESSION_TTL_SECONDS:
        new_timestamp = now
        set_session_cookie(response, user_id, new_timestamp)
        timestamp = new_timestamp

    return {
        "user_id": user_id,
        "username": VALID_USERNAME,
        "last_activity": timestamp,
    }


def get_common_headers(
    user_agent: str | None = Header(default=None),
    accept_language: str | None = Header(default=None),
) -> CommonHeaders:
    if not user_agent or not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Missing required headers: User-Agent and Accept-Language",
        )

    try:
        return CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/headers")
def read_headers(headers: CommonHeaders = Depends(get_common_headers)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@app.get("/info")
def read_info(
    response: Response,
    headers: CommonHeaders = Depends(get_common_headers),
):
    response.headers["X-Server-Time"] = datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
