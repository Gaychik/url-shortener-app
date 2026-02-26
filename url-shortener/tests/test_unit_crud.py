"""
Unit тесты для модуля crud.py
"""
import pytest
from app import crud, schemas
from app.models import User, Link
from sqlalchemy.orm import Session


class TestUserCRUD:
    """Тесты для операций с пользователями."""

    def test_create_user(self, db: Session):
        """Проверяем создание нового пользователя."""
        user_data = schemas.UserCreate(
            email="newuser@example.com",
            password="password123"
        )
        
        user = crud.create_user(db=db, user=user_data)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.hashed_password != "password123"  # Пароль должен быть хеширован

    def test_create_user_unique_email(self, db: Session):
        """Проверяем, что email уникален."""
        user_data = schemas.UserCreate(
            email="unique@example.com",
            password="password123"
        )
        
        crud.create_user(db=db, user=user_data)
        
        # Пытаемся создать пользователя с тем же email
        # SQLAlchemy должен вызвать ошибку
        with pytest.raises(Exception):  # IntegrityError
            crud.create_user(db=db, user=user_data)
            db.commit()

    def test_get_user_by_email(self, db: Session, test_user):
        """Проверяем получение пользователя по email."""
        user = crud.get_user_by_email(db=db, email=test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    def test_get_user_by_email_not_found(self, db: Session):
        """Проверяем получение несуществующего пользователя."""
        user = crud.get_user_by_email(db=db, email="nonexistent@example.com")
        
        assert user is None


class TestLinkCRUD:
    """Тесты для операций со ссылками."""

    def test_create_short_link(self, db: Session):
        """Проверяем создание короткой ссылки."""
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/very/long/url"
        )
        
        link = crud.create_short_link(db=db, link=link_data)
        
        assert link.id is not None
        assert link.short_code is not None
        assert len(link.short_code) == 7  # MD5 хеш первые 7 символов
        assert link.original_url == "https://www.example.com/very/long/url"

    def test_create_short_link_same_url_returns_same_code(self, db: Session):
        """Проверяем, что одного URL дважды не создается."""
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/test"
        )
        
        link1 = crud.create_short_link(db=db, link=link_data)
        link2 = crud.create_short_link(db=db, link=link_data)
        
        assert link1.short_code == link2.short_code
        assert link1.id == link2.id  # Должна быть одна и та же ссылка

    def test_create_short_link_with_owner(self, db: Session, test_user):
        """Проверяем создание ссылки с привязкой к пользователю."""
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/owned_link"
        )
        link_data.owner_id = test_user.id
        
        link = crud.create_short_link(db=db, link=link_data)
        
        assert link.owner_id == test_user.id

    def test_get_link_by_short_code(self, db: Session):
        """Проверяем получение ссылки по короткому коду."""
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/test"
        )
        created_link = crud.create_short_link(db=db, link=link_data)
        
        found_link = crud.get_link_by_short_code(db=db, short_code=created_link.short_code)
        
        assert found_link is not None
        assert found_link.id == created_link.id
        assert found_link.original_url == created_link.original_url

    def test_get_link_by_short_code_not_found(self, db: Session):
        """Проверяем получение несуществующей ссылки."""
        link = crud.get_link_by_short_code(db=db, short_code="nonexistent")
        
        assert link is None

    def test_get_link_by_original_url(self, db: Session):
        """Проверяем получение ссылки по оригинальному URL."""
        original_url = "https://www.example.com/original"
        link_data = schemas.LinkCreate(
            original_url=original_url
        )
        created_link = crud.create_short_link(db=db, link=link_data)
        
        found_link = crud.get_link_by_original_url(db=db, original_url=original_url)
        
        assert found_link is not None
        assert found_link.id == created_link.id

    def test_get_user_links(self, db: Session, test_user):
        """Проверяем получение всех ссылок пользователя."""
        # Создаем несколько ссылок для пользователя
        link_data1 = schemas.LinkCreate(
            original_url="https://www.example.com/link1"
        )
        link_data1.owner_id = test_user.id
        
        link_data2 = schemas.LinkCreate(
            original_url="https://www.example.com/link2"
        )
        link_data2.owner_id = test_user.id
        
        crud.create_short_link(db=db, link=link_data1)
        crud.create_short_link(db=db, link=link_data2)
        
        # Получаем все ссылки пользователя
        user_links = crud.get_user_links(db=db, user_id=test_user.id)
        
        assert len(user_links) == 2

    def test_get_user_links_empty(self, db: Session, test_user):
        """Проверяем получение ссылок для пользователя без ссылок."""
        user_links = crud.get_user_links(db=db, user_id=test_user.id)
        
        assert len(user_links) == 0


class TestClickCRUD:
    """Тесты для регистрации кликов."""

    def test_create_click_record(self, db: Session):
        """Проверяем создание записи о клике."""
        # Сначала создаем ссылку
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/test"
        )
        link = crud.create_short_link(db=db, link=link_data)
        
        # Создаем mock request object
        from unittest.mock import Mock
        request = Mock()
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "Mozilla/5.0"
        
        # Создаем запись о клике
        click = crud.create_click_record(db=db, link_id=link.id, request=request)
        
        assert click.id is not None
        assert click.link_id == link.id
        assert click.ip_address == "192.168.1.1"
        assert click.user_agent == "Mozilla/5.0"

    def test_get_link_stats(self, db: Session):
        """Проверяем получение статистики ссылки."""
        # Сначала создаем ссылку
        link_data = schemas.LinkCreate(
            original_url="https://www.example.com/test"
        )
        link = crud.create_short_link(db=db, link=link_data)
        
        # Создаем несколько кликов
        from unittest.mock import Mock
        request = Mock()
        request.client.host = "192.168.1.1"
        request.headers.get.return_value = "Mozilla/5.0"
        
        crud.create_click_record(db=db, link_id=link.id, request=request)
        crud.create_click_record(db=db, link_id=link.id, request=request)
        crud.create_click_record(db=db, link_id=link.id, request=request)
        
        # Получаем статистику
        stats = crud.get_link_stats(db=db, link_id=link.id)
        
        assert stats["total_clicks"] == 3
