from aiogram.types import Message, CallbackQuery
from aiogram import Bot
from aiogram.filters import CommandObject

from core.handlers.utils import START_SPEECH
from core.settings import bot_commands
from core.keyboards import MAIN_MENU_BOARD


# @router.startup()
# async def start_bot(bot: Bot):
#     await bot.send_message(settings.bots.admin_id, text="Бот запущен!")

# @router.shutdown()
# async def stop_bot(bot: Bot):
#     await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")


async def get_start(message: Message):
    await message.answer(START_SPEECH, reply_markup=MAIN_MENU_BOARD)


async def help_command(message: Message, bot: Bot, command: CommandObject):
    if command.args:
        for cmd in bot_commands:
            if cmd[0] == command.args:
                return await message.answer(
                    f"{cmd[0]} - {cmd[1]}\n\n{cmd[2]}"
                )
            else:
                return await message.answer("Команда не найдена", reply_markup=MAIN_MENU_BOARD)
    return await help_func(message)


async def help_func(message: Message):
    return await message.answer(
        "Помощь и справка о боте\n"
        "Для того чтобы получить информацию о команде используй /help `команда`\n", reply_markup=MAIN_MENU_BOARD
    )


async def menu_command(message: Message):
    await message.answer("Выберите действие из основного меню:", reply_markup=MAIN_MENU_BOARD)


async def noop_callback_handler(callback_query: CallbackQuery):
    await callback_query.answer(cache_time=60)
