from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import dotenv 
dotenv.load_dotenv()
# Используем переменную окружения DATABASE_URL или SQLite по умолчанию для разработки
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./test.db"  # SQLite для разработки/тестирования
)

# Для SQLite нужны дополнительные параметры
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Для PostgreSQL
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
