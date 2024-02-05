"""
    Структура клавиатуры отмены
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


CHOOSE_FIELD_TO_EDIT = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Перевод", callback_data="card_edit_translation")],
        [InlineKeyboardButton(text="Транскрипция", callback_data="card_edit_transcription")],
        [InlineKeyboardButton(text="Контекст", callback_data="card_edit_example_usage")],
])
