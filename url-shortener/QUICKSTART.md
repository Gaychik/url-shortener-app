## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск приложения
```bash
python run.py
```

Приложение запустится на `http://127.0.0.1:8000`

### 3. Документация API
Откройте в браузере: `http://127.0.0.1:8000/docs`

### 4. Запуск тестов
```bash
# Все тесты
pytest -v

# Только integration тесты
pytest tests/test_integration.py -v

# Только unit тесты
pytest tests/test_unit_auth.py tests/test_unit_crud.py -v
```

---

## 📝 Примеры API запросов

### Создать публичную ссылку
```bash
curl -X POST "http://localhost:8000/api/links" \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://github.com"}'
```

### Зарегистрировать пользователя
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

### Логиниться
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=pass123"
```

---

**Всё готово к работе!** 🎉
