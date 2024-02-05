# Создаём фильтр для данных колбэка пагинации
import datetime

from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker

from core.db import (
    get_cards_for_repetition,
    get_repetitions_by_card_id,
    LEVEL_TO_COLOR,
    LEVEL_TO_PERCENT,
    update_repetition
)
from core.handlers.paginations import Pagination
from core.keyboards import MAIN_MENU_BOARD


async def on_details_repetition(callback_query: CallbackQuery, session_maker: sessionmaker):
    """
    :param
    """
    user_id = callback_query.from_user.id
    today = datetime.date.today()
    cards_for_review = await get_cards_for_repetition(session_maker, user_id, today)
    if not cards_for_review:
        await callback_query.message.answer(f"На сегодня повторений нет 🙌", reply_markup=MAIN_MENU_BOARD)
        return

    pagination = Pagination(cards_for_review, page_size=1)
    current_page_cards = pagination.get_current_page_items()

    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0]

    current_page_cards = pagination.get_current_page_items()
    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0]

    result = "\n".join(
        f"▫️ {card.foreign_word} - <tg-spoiler>{card.translation}</tg-spoiler>\n\n{LEVEL_TO_COLOR[repetition.level]}"
        f"({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
        for card in pagination.get_current_page_items()
    )
    await callback_query.message.answer(f"Повторения:\n\n{result}",
                                        reply_markup=pagination.update_kb_repetition_detail(repetition.id))


async def on_details_repetition_pagination(callback_query: CallbackQuery, session_maker: sessionmaker):
    """
    Обрабатывает пагинацию для деталей повторений.
    """
    # Разбор данных колбэка для получения идентификатора повторения и действия
    # repetition_detail_page
    data_parts = callback_query.data.split('_')
    page_action = data_parts[2]
    page_number = int(data_parts[3])

    user_id = callback_query.from_user.id
    today = datetime.date.today()

    # Получаем карточки для повторения
    cards_for_review = await get_cards_for_repetition(session_maker, user_id, today)
    if not cards_for_review:
        await callback_query.message.answer("На сегодня повторений нет 🙌", reply_markup=MAIN_MENU_BOARD)
        return

    # Инициализация пагинации
    pagination = Pagination(cards_for_review, page_size=1)
    pagination.current_page = page_number

    # Получаем текущие карточки на странице и информацию о повторениях
    current_page_cards = pagination.get_current_page_items()
    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0] if repetitions_info else None

    # Составляем сообщение с деталями повторений
    if repetition:
        result = "\n".join(
            f"▫️ {card.foreign_word} - <tg-spoiler>{card.translation}</tg-spoiler>\n\n{LEVEL_TO_COLOR[repetition.level]}"
            f"({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
            for card in current_page_cards
        )
        await callback_query.message.edit_text(f"Повторения:\n\n{result}",
                                               reply_markup=pagination.update_kb_repetition_detail(repetition.id))
    else:
        await callback_query.message.edit_text("Детали повторения не найдены.")

    await callback_query.answer()


async def on_approve_repetition(callback_query: CallbackQuery, session_maker: sessionmaker):
    """
    Обновляет статус повторения на успешно выполненный.
    """
    repetition_id = int(callback_query.data.split('_')[2])
    await update_repetition(session_maker, repetition_id, success=True)
    await callback_query.message.answer("Отлично!\nКарточка успешно была повторена.")
