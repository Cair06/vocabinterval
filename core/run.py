import pathlib
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
# from aioredis import Redis
import asyncio
import logging

from sqlalchemy import URL
from middlewares.register_check import RegisterCheck

from settings import settings, bot_commands, porstgres_url
# from core.handlers.start import router

from db import create_async_engine, get_session_maker
from handlers import register_user_commands


    
    

async def bot_start(logger: logging.Logger) -> None:
    try:
        logging.basicConfig(level=logging.DEBUG)
        
        commands_for_bot = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]

        # redis = Redis()

        dp = Dispatcher(storage=MemoryStorage())

        dp.message.middleware(RegisterCheck())
        dp.callback_query.middleware(RegisterCheck())
        
        bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
        register_user_commands(dp)
        await bot.set_my_commands(commands=commands_for_bot)

        async_engine = create_async_engine(porstgres_url)
        session_maker = get_session_maker(async_engine)
        # Деллегировано alembic
        # await proceed_schemas(async_engine, BaseModel.metadata)
        
        await dp.start_polling(bot, session_maker=session_maker)
    finally:
        await bot.session.close()
        
         
def setup_env():
    """Настройка переменных окружения"""
    from dotenv import load_dotenv
    path = pathlib.Path(__file__).parent.parent
    dotenv_path = path.joinpath('.env')
    if dotenv_path.exists():
        load_dotenv(dotenv_path)


def main():
    """Функция для запуска через poetry"""
    logger = logging.getLogger(__name__)
    try:
        setup_env()
        asyncio.run(bot_start(logger))
        logger.info('Bot started')
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped')


if __name__ == '__main__':
    main()