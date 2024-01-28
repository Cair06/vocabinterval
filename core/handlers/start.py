from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, F
from aiogram import Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder, InlineKeyboardBuilder
)

from core.structures.fsm_group import CardStates
from core.settings import settings, bot_commands
from sqlalchemy.orm import sessionmaker

from core.db import get_all_user_cards
from .paginations import Pagination#, get_pagination_keyboard

# router = Router()


# @router.startup()
# async def start_bot(bot: Bot):
#     await bot.send_message(settings.bots.admin_id, text="Бот запущен!")

# @router.shutdown()
# async def stop_bot(bot: Bot):
#     await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")


async def get_start(message: Message):
    menu_builder = ReplyKeyboardBuilder()
    menu_builder.button(
        text="Помощь"
    )
    menu_builder.button(
        text="Словарь"
    )
    menu_builder.button(
        text="Добавить карточку"
    )
    await message.answer(
        "Меню",
        reply_markup=menu_builder.as_markup(resize_keyboard=True)
    )

async def help_command(message: Message, bot: Bot, command: CommandObject):
    if command.args:
        for cmd in bot_commands:
            if cmd[0] == command.args:
                return await message.answer(
                    f"{cmd[0]} - {cmd[1]}\n\n{cmd[2]}"
                )
            else:
                return await message.answer("Команда не найдена")
    return await help_func(message)
            

    
async def help_func(message: Message):
    return await message.answer(
        "Помощь и справка о боте\n"
        "Для того чтобы получить информацию о команде используй /help `команда`\n"
    )



async def noop_callback_handler(callback_query: CallbackQuery):
    await callback_query.answer(cache_time=60)