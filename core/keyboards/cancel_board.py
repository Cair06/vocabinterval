"""
    Структура клавиатуры отмены
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


CANCEL_BOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отмена'), ],
    ],
    resize_keyboard=True
)

CANCEL_AND_NEXT_BOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отмена'), 
         KeyboardButton(text="Продолжить")
         ],
    ],
    resize_keyboard=True
)