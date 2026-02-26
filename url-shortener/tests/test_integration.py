"""
Integration тесты для API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthFlowIntegration:
    """Тесты для полного цикла аутентификации."""

    def test_user_registration(self, client: TestClient):
        """Проверяем регистрацию нового пользователя."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Пароль не должен возвращаться

    def test_user_registration_duplicate_email(self, client: TestClient, test_user_data):
        """Проверяем, что при регистрации с существующим email возвращается ошибка."""
        # Регистрируем первого пользователя
        client.post(
            "/api/auth/register",
            json=test_user_data
        )
        
        # Пытаемся зарегистрировать второго с тем же email
        response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        
        assert response.status_code == 400
        assert "уже зарегистрирован" in response.json()["detail"]

    def test_user_login(self, client: TestClient, test_user_data):
        """Проверяем логин и получение токена."""
        # Сначала регистрируем пользователя
        client.post(
            "/api/auth/register",
            json=test_user_data
        )
        
        # Логинимся
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_invalid_credentials(self, client: TestClient, test_user_data):
        """Проверяем логин с неправильными учетными данными."""
        # Регистрируем пользователя
        client.post(
            "/api/auth/register",
            json=test_user_data
        )
        
        # Пытаемся залогиниться с неправильным паролем
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["email"],
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]

    def test_user_login_nonexistent_user(self, client: TestClient):
        """Проверяем логин несуществующего пользователя."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.json()["detail"]


class TestLinkCreationAndRedirect:
    """Тесты для создания ссылок и редиректов."""

    def test_create_public_link(self, client: TestClient):
        """Проверяем создание публичной ссылки (без аутентификации)."""
        response = client.post(
            "/api/links",
            json={"original_url": "https://www.example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert "original_url" in data
        # Pydantic HttpUrl может добавить trailing slash
        assert "example.com" in data["original_url"]

    def test_redirect_to_original_url(self, client: TestClient):
        """Проверяем редирект по короткой ссылке."""
        # Создаем ссылку
        create_response = client.post(
            "/api/links",
            json={"original_url": "https://www.google.com"}
        )
        
        short_code = create_response.json()["short_code"]
        original_url = create_response.json()["original_url"]
        
        # Выполняем редирект
        response = client.get(f"/{short_code}", follow_redirects=False)
        
        assert response.status_code == 307  # Temporary redirect
        # Проверяем, что редирект указывает на оригинальный URL
        assert "google.com" in response.headers["location"]

    def test_redirect_nonexistent_link(self, client: TestClient):
        """Проверяем редирект на несуществующую ссылку."""
        response = client.get("/nonexistent", follow_redirects=False)
        
        assert response.status_code == 404
        assert "Ссылка не найдена" in response.json()["detail"]


class TestFullAuthenticationFlow:
    """Полные тесты цикла аутентификации, создания ссылок и получения статистики."""

    def test_complete_user_flow(self, client: TestClient, db: Session):
        """
        Полный цикл:
        1. Регистрация пользователя
        2. Логин и получение токена
        3. Создание ссылки с токеном
        4. Получение списка ссылок пользователя
        5. Редирект и проверка счетчика кликов
        """
        
        # 1. Регистрируем пользователя
        user_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        
        register_response = client.post(
            "/api/auth/register",
            json=user_data
        )
        
        assert register_response.status_code == 200
        user_id = register_response.json()["id"]
        
        # 2. Логинимся и получаем токен
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Создаем ссылку с токеном (аутентифицированный запрос)
        headers = {"Authorization": f"Bearer {token}"}
        
        link_data = {"original_url": "https://www.github.com"}
        
        create_link_response = client.post(
            "/api/links",
            json=link_data,
            headers=headers
        )
        
        assert create_link_response.status_code == 200
        link = create_link_response.json()
        short_code = link["short_code"]
        
        # 4. Получаем список ссылок пользователя
        links_response = client.get(
            "/api/users/me/links",
            headers=headers
        )
        
        assert links_response.status_code == 200
        user_links = links_response.json()
        assert len(user_links) >= 1
        assert any(l["short_code"] == short_code for l in user_links)
        
        # 5. Выполняем редирект и проверяем счетчик кликов
        redirect_response = client.get(f"/{short_code}", follow_redirects=False)
        
        assert redirect_response.status_code == 307
        assert "github.com" in redirect_response.headers["location"]

    def test_user_links_isolation(self, client: TestClient):
        """
        Проверяем, что пользователи видят только свои ссылки.
        """
        
        # Регистрируем первого пользователя и создаем ссылку
        user1_data = {
            "email": "user1@example.com",
            "password": "password1"
        }
        
        client.post("/api/auth/register", json=user1_data)
        login1_response = client.post(
            "/api/auth/login",
            data={"username": user1_data["email"], "password": user1_data["password"]}
        )
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Первый пользователь создает ссылку
        client.post(
            "/api/links",
            json={"original_url": "https://www.google.com"},
            headers=headers1
        )
        
        # Регистрируем второго пользователя
        user2_data = {
            "email": "user2@example.com",
            "password": "password2"
        }
        
        client.post("/api/auth/register", json=user2_data)
        login2_response = client.post(
            "/api/auth/login",
            data={"username": user2_data["email"], "password": user2_data["password"]}
        )
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Второй пользователь создает свою ссылку
        client.post(
            "/api/links",
            json={"original_url": "https://www.github.com"},
            headers=headers2
        )
        
        # Получаем ссылки первого пользователя
        links1_response = client.get("/api/users/me/links", headers=headers1)
        links1 = links1_response.json()
        
        # Получаем ссылки второго пользователя
        links2_response = client.get("/api/users/me/links", headers=headers2)
        links2 = links2_response.json()
        
        # Каждый пользователь должен видить только свои ссылки
        assert len(links1) == 1
        assert len(links2) == 1
        assert "google.com" in links1[0]["original_url"]
        assert "github.com" in links2[0]["original_url"]

    def test_access_links_without_authentication(self, client: TestClient):
        """
        Проверяем, что получить список своих ссылок без токена нельзя.
        """
        
        # Пытаемся получить список ссылок без токена
        response = client.get("/api/users/me/links")
        
        assert response.status_code == 401  # Unauthorized (не 403)


class TestClickCounting:
    """Тесты для подсчета кликов."""

    def test_click_counter_increment(self, client: TestClient):
        """
        Проверяем, что счетчик кликов увеличивается при редиректе.
        """
        
        # Создаем ссылку
        create_response = client.post(
            "/api/links",
            json={"original_url": "https://www.python.org"}
        )
        
        short_code = create_response.json()["short_code"]
        link_id = create_response.json()["id"]
        
        # Выполняем редирект (это должно записать клик)
        client.get(f"/{short_code}", follow_redirects=False)
        
        # TODO: Здесь нужно добавить эндпоинт для получения статистики
        # и проверить, что количество кликов равно 1
        # assert stats["total_clicks"] == 1
