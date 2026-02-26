from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

# --- Схемы для кликов ---

class ClickResponse(BaseModel):
    id: int
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    country: Optional[str] = None
    device: Optional[str] = None

    class Config:
        orm_mode = True

# --- Схемы для ссылок ---

# Схема для создания ссылки (что мы принимаем от пользователя)
class LinkCreate(BaseModel):
    original_url: HttpUrl  # Pydantic проверит, что это валидный URL
    owner_id: Optional[int] = None  # Опциональный ID владельца
    expiration_date: Optional[datetime] = None

# Схема для ответа (что мы отдаем пользователю)
class LinkResponse(BaseModel):
    id: int
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    expiration_date: Optional[datetime] = None
    total_clicks: int = 0
    clicks: List[ClickResponse] = []

    class Config:
        orm_mode = True  # Позволяет Pydantic работать с моделями SQLAlchemy

# --- Схемы для пользователей ---

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

# --- Схемы для токенов ---

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Схема для ответа со статистикой
class LinkStats(BaseModel):
    total_clicks: int
