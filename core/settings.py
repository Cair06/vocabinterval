import os
from dotenv import load_dotenv
from dataclasses import dataclass

from sqlalchemy import URL

bot_commands = (
    ("start", "Начало работы с ботом", "Хорошая команда, чтобы начать работу с ботом"),
    ("help", "Помощь и справка", "Поможет если это будет необходимо")
)



load_dotenv()


porstgres_url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv("DB_USER"),
    host="localhost",
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT")
)

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