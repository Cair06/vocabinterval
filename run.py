from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging

from sqlalchemy import URL
from core.middlewares.register_check import RegisterCheck

from core.settings import settings, bot_commands, porstgres_url
# from core.handlers.start import router

from core.db import create_async_engine, get_session_maker
from core.handlers import register_user_commands


    
    

async def start():
    try:
        logging.basicConfig(level=logging.DEBUG)

        bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
        
        commands_for_bot = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in bot_commands]

        dp = Dispatcher(storage=MemoryStorage())

        dp.message.middleware(RegisterCheck())
        dp.callback_query.middleware(RegisterCheck())
        register_user_commands(dp)



        await bot.set_my_commands(commands=commands_for_bot)

        async_engine = create_async_engine(porstgres_url)
        session_maker = get_session_maker(async_engine)
        # Деллегировано alembic
        # await proceed_schemas(async_engine, BaseModel.metadata)
        
        await dp.start_polling(bot, session_maker=session_maker)
    finally:
        await bot.session.close()
        
         
if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("Exit")
        