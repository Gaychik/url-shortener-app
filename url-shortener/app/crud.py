import hashlib
import uuid
from sqlalchemy.orm import Session
from fastapi import Request
from . import models, schemas

def get_link_by_short_code(db: Session, short_code: str):
    """Возвращает объект ссылки по ее короткому коду."""
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()

def get_link_by_original_url(db: Session, original_url: str):
    """Возвращает объект ссылки по ее оригинальному URL."""
    return db.query(models.Link).filter(models.Link.original_url == original_url).first()

def create_short_link(db: Session, link: schemas.LinkCreate, owner_id: int | None = None):
    """Создает короткую ссылку в базе данных."""
    original = str(link.original_url)
    owner = owner_id if owner_id is not None else link.owner_id

    # Если указан владелец — переиспользуем ссылку только если она принадлежит тому же владельцу
    if owner is not None:
        db_link = db.query(models.Link).filter(models.Link.original_url == original, models.Link.owner_id == owner).first()
        if db_link:
            return db_link

    # Для новых записей (анонимных или других владельцев) — всегда создаём новую короткую ссылку.
    # Генерация: md5 от (URL|owner|random_uuid) — чтобы разные пользователи получали разные short_code для одного ресурса.
    short_code = None
    for _ in range(5):
        seed = f"{original}|{owner}|{uuid.uuid4().hex}"
        candidate = hashlib.md5(seed.encode()).hexdigest()[:7]
        exists = db.query(models.Link).filter(models.Link.short_code == candidate).first()
        if not exists:
            short_code = candidate
            break

    if short_code is None:
        # В очень редком случае используем uuid как запасной вариант
        short_code = uuid.uuid4().hex[:7]

    db_link = models.Link(
        original_url=original,
        short_code=short_code,
        owner_id=owner, # Добавляем owner_id
        expiration_date=link.expiration_date # Добавляем дату истечения
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

from .auth import get_password_hash

# --- Функции для Пользователей ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_links(db: Session, user_id: int):
    """Возвращает все ссылки, созданные пользователем."""
    return db.query(models.Link).filter(models.Link.owner_id == user_id).all()

def create_click_record(db: Session, link_id: int, request: Request):
    """Создает запись о клике в БД."""
    # Примечание: определение страны и устройства - более сложная задача.
    # Для страны (GeoIP) нужна база данных IP-адресов (например, GeoLite2 от MaxMind).
    # Для устройства нужен парсинг заголовка User-Agent.
    # Пока мы сохраним только IP и User-Agent.
    
    db_click = models.Click(
        link_id=link_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(db_click)
    db.commit()
    db.refresh(db_click)
    return db_click

def get_link_stats(db: Session, link_id: int):
    """Возвращает количество кликов для ссылки."""
    # Это простая реализация. В реальном проекте здесь будет агрегация
    # по дням, странам и т.д.
    count = db.query(models.Click).filter(models.Click.link_id == link_id).count()
    return {"total_clicks": count}