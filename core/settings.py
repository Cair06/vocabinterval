import os
from dotenv import load_dotenv
from dataclasses import dataclass

from sqlalchemy import URL


bot_commands = (
    ("start", "Начало работы с ботом", "Хорошая команда, чтобы начать работу с ботом"),
    ("help", "Помощь и справка", "Поможет если это будет необходимо"),
    ("get_card", "Получение карточки, используйте /get_card <слово>",
     "Выводит дополнительную информацию для определенной карточки. Используйте /get_card <слово>"),
)

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_HOST = os.getenv("POSTGRES_HOST", "db")

postgres_url = URL.create(
    "postgresql+asyncpg",
    username=DB_USER,
    host=DB_HOST,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT
)

# Настройки подключения к Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Используйте localhost для локального подключения
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_USER = os.getenv("REDIS_USER", None)

redis_settings = {
    "host": REDIS_HOST,
    "password": REDIS_PASSWORD,
    "username": REDIS_USER,
}


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    sql_alchemy_url: str


@dataclass
class Settings:
    bots: Bots


def get_settings():
    return Settings(bots=Bots(
        bot_token=os.getenv("TOKEN"),
        admin_id=os.getenv("ADMIN_ID"),
        sql_alchemy_url=os.getenv("SQL_ALCHEMY_URL")
    ))


settings = get_settings()
