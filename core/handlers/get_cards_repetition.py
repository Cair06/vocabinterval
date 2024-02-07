# Создаём фильтр для данных колбэка пагинации
import datetime

from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker

from core.db import get_cards_for_repetition, get_repetitions_by_card_id, LEVEL_TO_COLOR, LEVEL_TO_PERCENT
from core.keyboards import MAIN_MENU_BOARD
from .paginations import Pagination
from .utils import menu_text


async def on_repetition_cards_start(message: Message, session_maker: sessionmaker):
    user_id = message.from_user.id
    today = datetime.date.today()
    cards_for_review = await get_cards_for_repetition(session_maker, user_id, today)
    if not cards_for_review:
        await message.answer("На сегодня повторений нет 🙌", reply_markup=MAIN_MENU_BOARD)
        return

    pagination = Pagination(cards_for_review, page_size=10)
    current_page_cards = pagination.get_current_page_items()

    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0]

    result = ("📚 Список для повторения:\n\n" +
              "\n".join(
                  f"▫️ {card.foreign_word} - {LEVEL_TO_COLOR[repetition.level]}"
                  f"({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
                  for card in pagination.get_current_page_items()
              ) + menu_text)

    await message.answer(result, reply_markup=pagination.update_kb_repetitions())


async def on_repetition_cards_pagination(callback_query: CallbackQuery, session_maker: sessionmaker):
    # cards_repetitions_page_2
    print(f"Received callback: {callback_query.data}")  # Добавить для отладки
    page_action, page_number = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    page_number = int(page_number)
    print(f"page_numb: {page_number}")  # Добавить для отладки

    user_id = callback_query.from_user.id
    today = datetime.date.today()
    cards_for_review = await get_cards_for_repetition(session_maker, user_id, today)

    pagination = Pagination(cards_for_review, page_size=10)
    pagination.current_page = page_number
    current_page_cards = pagination.get_current_page_items()

    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0]

    result = ("📚 Список для повторения:\n\n" +
              "\n".join(
                  f"▫️ {card.foreign_word} - {LEVEL_TO_COLOR[repetition.level]}"
                  f"({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
                  for card in pagination.get_current_page_items()) + menu_text )

    await callback_query.message.edit_text(result, reply_markup=pagination.update_kb_repetitions())
    await callback_query.answer()
