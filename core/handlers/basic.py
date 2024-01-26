from aiogram.types import Message, ContentType
from aiogram import Bot, Dispatcher, F
from aiogram import Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder, InlineKeyboardBuilder
)


from core.settings import settings, bot_commands


router = Router()


@router.startup()
async def start_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Бот запущен!")

@router.shutdown()
async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")



@router.message(CommandStart())
async def get_start(message: Message, bot: Bot):
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

@router.message(Command(commands=["help"]))
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
            

    
@router.message(F.text=="Помощь")
async def help_func(message: Message):
    return await message.answer(
        "Помощь и справка о боте\n"
        "Для того чтобы получить информацию о команде используй /help `команда`\n"
    )
    
@router.message(F.text=="Словарь")
async def help_func(message: Message):
    return await message.answer(
            "Словарь:\n"
            "▫️family 🔁 <tg-spoiler>семья, округа\n"
            "— I love my family\n"
            "— I deserve my family</tg-spoiler>"
            )

@router.message(F.text=="Добавить карточку")
async def help_func(message: Message):
    return await message.answer("Тут вы сможете добавить карточку")