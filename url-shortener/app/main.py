from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from . import auth
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Эта команда создает таблицы в БД на основе моделей, если их еще нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Сервис коротких ссылок",
    description="API для сервиса создания коротких ссылок с аналитикой."
)

origins = [
    "http://localhost:5173"  # Ваш frontend на Vite
    
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешаем указанные origins
    allow_credentials=True, # Разрешаем передачу cookies/авторизационных заголовков
    allow_methods=["*"],    # Разрешаем все методы (GET, POST, etc.)
    allow_headers=["*"],    # Разрешаем все заголовки
)
# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Эндпоинты ---

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API сервиса коротких ссылок!"}

@app.post("/api/links", response_model=schemas.LinkResponse, summary="Создание короткой ссылки")
def create_link(
    link: schemas.LinkCreate,
    db: Session = Depends(get_db),
    current_user: Optional[schemas.UserResponse] = Depends(auth.get_current_user_optional)
):
    """
    Создает новую короткую ссылку.
    Если пользователь аутентифицирован, ссылка будет привязана к его аккаунту.
    """
    # Определяем владельца по токену (если есть) и передаём в CRUD
    owner_id = current_user.id if current_user else None
    return crud.create_short_link(db=db, link=link, owner_id=owner_id)


@app.get("/{short_code}", summary="Редирект по короткой ссылке")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Перенаправляет пользователя на оригинальный URL.
    Здесь же происходит сбор статистики о кликах.
    """
    db_link = crud.get_link_by_short_code(db, short_code=short_code)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    # Проверяем, не истек ли срок жизни ссылки
    if db_link.expiration_date:
        now = datetime.now(timezone.utc)
        expiration = db_link.expiration_date
        # Приводим обе даты к одному формату для сравнения
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        if expiration < now:
            raise HTTPException(status_code=410, detail="Срок действия ссылки истек")

    # Записываем клик
    crud.create_click_record(db, link_id=db_link.id, request=request)

    return RedirectResponse(url=db_link.original_url)


@app.post("/api/auth/register", response_model=schemas.UserResponse, summary="Регистрация нового пользователя")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового пользователя.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован")
    return crud.create_user(db=db, user=user)


@app.post("/api/auth/login", response_model=schemas.Token, summary="Аутентификация пользователя и получение токена")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Аутентифицирует пользователя и возвращает JWT токен.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me/links", response_model=List[schemas.LinkResponse], summary="Получить все ссылки пользователя")
def get_user_links(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.get_current_user)
):
    """
    Возвращает все ссылки, созданные текущим аутентифицированным пользователем.
    """
    return crud.get_user_links(db=db, user_id=current_user.id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
