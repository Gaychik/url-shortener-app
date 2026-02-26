"""
Unit тесты для модуля auth.py
"""
import pytest
from app.auth import get_password_hash, verify_password, create_access_token
from jose import jwt
from app.auth import SECRET_KEY, ALGORITHM
from datetime import timedelta, datetime


class TestPasswordHashing:
    """Тесты для хеширования паролей."""

    def test_get_password_hash_returns_string(self):
        """Проверяем, что get_password_hash возвращает строку."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_different_for_same_password(self):
        """Проверяем, что один и тот же пароль хешируется по-разному (из-за соли)."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Хэши должны быть разными из-за разной соли в bcrypt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Проверяем, что verify_password возвращает True для правильного пароля."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Проверяем, что verify_password возвращает False для неправильного пароля."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_contains_salt(self):
        """Проверяем, что хеш содержит соль (bcrypt хеш начинается с $2b$)."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # bcrypt хеши начинаются с $2b$, $2a$ или $2x$ или $2y$
        assert hashed.startswith(("$2a$", "$2b$", "$2x$", "$2y$"))


class TestJWTTokens:
    """Тесты для создания и проверки JWT токенов."""

    def test_create_access_token(self):
        """Проверяем, что create_access_token возвращает валидный JWT токен."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """Проверяем создание токена с пользовательским временем истечения."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        # Декодируем токен и проверяем, что он содержит нужные данные
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == "test@example.com"
        assert "exp" in payload

    def test_token_contains_email_claim(self):
        """Проверяем, что токен содержит email в claim 'sub'."""
        email = "test@example.com"
        data = {"sub": email}
        token = create_access_token(data=data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == email

    def test_token_expiration_time(self):
        """Проверяем, что токен имеет корректное время истечения."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Проверяем, что время истечения истекает примерно через 30 минут
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        current_time = datetime.utcnow()
        time_diff = (exp_time - current_time).total_seconds()
        
        # Должно быть примерно 1800 секунд (30 минут)
        # Добавляем 10 секунд толерантности
        assert 1790 < time_diff < 1810

    def test_token_without_expiration_delta(self):
        """Проверяем создание токена без указания времени истечения (используется default)."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
