"""
Точка входа для запуска приложения через Python
Используйте: python run.py
"""
import uvicorn

if __name__ == "__main__":
    # Запускаем приложение на 127.0.0.1:8000
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # Перезагрузка при изменении файлов (для разработки)
    )
