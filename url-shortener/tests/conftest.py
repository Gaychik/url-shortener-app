import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import sys
import os

# Добавляем родительскую директорию в путь, чтобы импортировать app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.main import app, get_db
from fastapi.testclient import TestClient
from app import auth, crud, schemas
from app.models import User

# Используем SQLite для тестов (не требует БД)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Переопределяем зависимость get_db для использования тестовой БД."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Создает тестовую БД для каждого теста."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Создает TestClient с переопределенной зависимостью get_db."""
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data():
    """Возвращает данные тестового пользователя."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture(scope="function")
def test_user(test_user_data):
    """Создает тестового пользователя в БД."""
    db = TestingSessionLocal()
    user = crud.create_user(
        db=db,
        user=schemas.UserCreate(**test_user_data)
    )
    yield user
    db.close()


@pytest.fixture(scope="function")
def auth_token(test_user_data):
    """Генерирует токен аутентификации для тестового пользователя."""
    token = auth.create_access_token(
        data={"sub": test_user_data["email"]}
    )
    return token

