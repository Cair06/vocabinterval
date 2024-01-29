"""
    Структура клавиатуры отмены
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


MAIN_MENU_BOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Помощь"),KeyboardButton(text="Словарь"),KeyboardButton(text="Добавить карточку")]
    ],
    resize_keyboard=True, one_time_keyboard=True
)
