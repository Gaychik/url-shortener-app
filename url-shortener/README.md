# URL Shortener Application

## Описание
REST API сервиса для создания коротких ссылок с аналитикой кликов.

## 🚀 Запуск приложения

### Способ 1: Запуск через run.py (рекомендуется)
Это самый простой способ запуска приложения:

```bash
python run.py
```

✅ Автоматически запускает `uvicorn` с режимом перезагрузки (reload mode)  
✅ Приложение будет доступно по адресу: `http://127.0.0.1:8000`

### Способ 2: Запуск прямо из main.py
Если вы используете модуль как пакет:

```bash
python -m app.main
```

### Способ 3: Запуск с uvicorn через консоль
```bash
uvicorn app.main:app --reload
```

### 📖 Документация API
После запуска приложения, документация доступна по адресу:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 🧪 Тестирование

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск всех тестов
```bash
pytest
```

### Запуск с подробным выводом
```bash
pytest -v
```

### Запуск конкретной группы тестов

#### Unit тесты для auth (хеширование паролей и JWT токены)
```bash
pytest tests/test_unit_auth.py -v
```

#### Unit тесты для crud (операции с БД)
```bash
pytest tests/test_unit_crud.py -v
```

#### Integration тесты API  
```bash
pytest tests/test_integration.py -v
```

### Запуск с показанием покрытия кода (требует pytest-cov)
```bash
pip install pytest-cov
pytest --cov=app tests/
```

## 📋 Структура тестов

### Unit тесты (tests/test_unit_auth.py)
✓ Проверка хеширования паролей: `get_password_hash()` возвращает строку с солью  
✓ Проверка верификации пароля: `verify_password()` правильно проверяет пароли  
✓ Проверка JWT токенов: создание, декодирование, время истечения  
✓ Проверка структуры токена и наличия email в claim 'sub'

**Классы тестов:**
- `TestPasswordHashing` - 5 тестов для работы с паролями
- `TestJWTTokens` - 5 тестов для JWT токенов

### Unit тесты (tests/test_unit_crud.py)
✓ Создание пользователей и проверка уникальности email  
✓ Создание и получение коротких ссылок  
✓ Создание записей о кликах и получение статистики  
✓ Проверка вспомогательных функций БД

**Классы тестов:**
- `TestUserCRUD` - 4 теста для операций с пользователями
- `TestLinkCRUD` - 8 тестов для операций со ссылками  
- `TestClickCRUD` - 2 теста для регистрации кликов

### Integration тесты (tests/test_integration.py)
✓ **Регистрация пользователя** - создание нового аккаунта  
✓ **Логин** - получение JWT токена  
✓ **Создание ссылки** - привязка к пользователю при аутентификации  
✓ **Получение списка ссылок** - только для аутентифицированных пользователей  
✓ **Редирект** - проверка что редирект работает и счетчик развивается  
✓ **Защита данных** - каждый пользователь видит только свои ссылки

**Классы тестов:**
- `TestAuthFlowIntegration` - 4 теста аутентификации
- `TestLinkCreationAndRedirect` - 3 теста создания и редиректа
- `TestFullAuthenticationFlow` - 3 полных сценария
- `TestClickCounting` - 1 тест подсчета кликов

## 🔑 API эндпоинты

### Публичные эндпоинты
- `GET /` - Приветственное сообщение
- `GET /{short_code}` - Редирект по короткой ссылке (с записью клика)

### Аутентификация
- `POST /api/auth/register` - Регистрация нового пользователя
  ```json
  {"email": "user@example.com", "password": "secure_password"}
  ```
- `POST /api/auth/login` - Логин и получение токена
  ```
  Form data: username=user@example.com&password=secure_password
  ```

### Ссылки
- `POST /api/links` - Создание короткой ссылки (опционально с аутентификацией)
  ```json
  {"original_url": "https://example.com"}
  ```
- `GET /api/users/me/links` - Получить все ссылки текущего пользователя (требует токен)

## 📝 Примеры использования

### 1. Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "MySecurePassword123"
  }'
```

### 2. Логин и получение токена
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=MySecurePassword123"
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Создание публичной ссылки
```bash
curl -X POST "http://localhost:8000/api/links" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com"}'
```

### 4. Создание ссылки с аутентификацией
```bash
curl -X POST "http://localhost:8000/api/links" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"original_url": "https://www.python.org"}'
```

### 5. Получение своих ссылок
```bash
curl -X GET "http://localhost:8000/api/users/me/links" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Редирект по короткой ссылке
```bash
curl -L "http://localhost:8000/abc123"  # Автоматический редирект
```

## 🗄️ База данных

### Развитие/Тестирование
По умолчанию используется **SQLite** (файл `test.db`). Можно запускать сразу без настройки БД.

### Production
Для использования PostgreSQL установите переменную окружения `DATABASE_URL`:

```bash
# PowerShell
$env:DATABASE_URL = "postgresql://user:password@localhost:5432/url_shortener"
python run.py

# Bash
export DATABASE_URL="postgresql://user:password@localhost:5432/url_shortener"
python run.py
```

Или обновите строку в `app/database.py`.

## 📦 Требования

- Python 3.8+
- FastAPI - веб-фреймворк
- SQLAlchemy - ORM для работы с БД  
- Pydantic - валидация данных
- PassLib + bcrypt - безопасное хеширование паролей
- python-jose - работа с JWT токенами
- pytest - фреймворк для тестирования
- httpx - HTTP клиент для тестов

Все зависимости указаны в `requirements.txt` и могут быть установлены одной командой:
```bash
pip install -r requirements.txt
```

## 🎯 Примеры тестовых сценариев

### Полный сценарий: Регистрация → Логин → Создание ссылок
Смотрите [test_complete_user_flow](tests/test_integration.py#L306) для полного примера.

### Проверка безопасности: Изоляция данных пользователей
Смотрите [test_user_links_isolation](tests/test_integration.py#L348) для проверки что пользователи видят только свои ссылки.

## 🚀 Дальнейшие улучшения

- [ ] Добавить эндпоинт для получения статистики ссылки (`GET /api/links/{short_code}/stats`)
- [ ] Добавить возможность удаления ссылок
- [ ] Добавить собранную статистику (страна, устройство, браузер) 
- [ ] Добавить разное время жизни ссылок  
- [ ] Добавить персональные кодовые префиксы
- [ ] Добавить рейт-лимитинг
- [ ] Добавить логирование
- [ ] Добавить CI/CD (GitHub Actions)

## 📄 Структура проекта

```
url-shortener/
├── app/
│   ├── __init__.py          # Инициализация пакета
│   ├── main.py              # Основное приложение FastAPI
│   ├── database.py          # Конфигурация БД
│   ├── models.py            # Модели SQLAlchemy
│   ├── schemas.py           # Схемы Pydantic
│   ├── crud.py              # Операции БД
│   └── auth.py              # Аутентификация и JWT
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Конфигурация pytest
│   ├── test_unit_auth.py    # Unit тесты для auth
│   ├── test_unit_crud.py    # Unit тесты для crud
│   └── test_integration.py  # Integration тесты
├── run.py                   # Точка входа для запуска
├── requirements.txt         # Зависимости
└── README.md               # Этот файл
```

---

**Готово к использованию! 🎉**

Запустите приложение: `python run.py`  
Запустите тесты: `pytest tests/`

