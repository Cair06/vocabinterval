import os
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage

import asyncio
import logging

from core.middlewares.register_check import RegisterCheck

from core.settings import settings, bot_commands, postgres_url, redis_settings

from core.db import create_async_engine, get_session_maker
from core.handlers import register_user_commands
from redis import asyncio as aioredis


async def bot_start(logger: logging.Logger) -> None:
    try:
        logging.basicConfig(level=logging.DEBUG)

        commands_for_bot = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]

        redis = aioredis.Redis(**redis_settings)

        dp = Dispatcher(storage=RedisStorage(redis=redis))

        dp.message.middleware(RegisterCheck())
        dp.callback_query.middleware(RegisterCheck())

        bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
        register_user_commands(dp)
        await bot.set_my_commands(commands=commands_for_bot)

        async_engine = create_async_engine(postgres_url)
        session_maker = get_session_maker(async_engine)
        # Деллегировано alembic
        # await proceed_schemas(async_engine, BaseModel.metadata)

        await dp.start_polling(bot, session_maker=session_maker, redis=redis)
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
