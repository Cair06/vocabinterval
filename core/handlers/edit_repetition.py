# Создаём фильтр для данных колбэка пагинации
import datetime

from aiogram.types import CallbackQuery
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
from .utils import menu_text


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

    result = ("Повторения:\n\n" +
              "\n".join(
                  f"▫️ {card.foreign_word}\n\n"
                  + (f"Транскрипция: {card.transcription}\n" if card.transcription else "")
                  + (f"Контекст: {card.example_usage}\n" if card.example_usage else "")
                  + f"Создано: {card.created_at}\n\n"
                  + f"{LEVEL_TO_COLOR[repetition.level]}({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
                  for card in pagination.get_current_page_items()
              ) + menu_text)

    inl_markup = pagination.update_kb_repetition_detail(repetition.id, current_page_cards[0].id)
    await callback_query.message.answer(result, reply_markup=inl_markup)
    await callback_query.answer(cache_time=60)


async def on_details_repetition_pagination(callback_query: CallbackQuery, session_maker: sessionmaker, current_page: int = None):
    """
    Обрабатывает пагинацию для деталей повторений.
    """
    # Разбор данных колбэка для получения идентификатора повторения и действия
    # repetition_detail_page
    if current_page is None:
        data_parts = callback_query.data.split('_')
        if len(data_parts) > 3:
            current_page = int(data_parts[3])
        else:
            current_page = 1  # Значение по умолчанию, если страница не указана


    user_id = callback_query.from_user.id
    today = datetime.date.today()

    # Получаем карточки для повторения
    cards_for_review = await get_cards_for_repetition(session_maker, user_id, today)
    if not cards_for_review:
        await callback_query.message.answer("На сегодня повторений нет 🙌", reply_markup=MAIN_MENU_BOARD)
        return

    # Инициализация пагинации
    pagination = Pagination(cards_for_review, page_size=1)
    pagination.current_page = current_page

    # Получаем текущие карточки на странице и информацию о повторениях
    current_page_cards = pagination.get_current_page_items()
    repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
    repetition = repetitions_info[0] if repetitions_info else None

    # Составляем сообщение с деталями повторений
    if repetition:
        result = (f"Повторения:\n\n" +
                  "\n".join(
                      f"▫️ {card.foreign_word}\n\n"
                      + (f"Транскрипция: {card.transcription}\n" if card.transcription else "")
                      + (f"Контекст: {card.example_usage}\n" if card.example_usage else "")
                      + f"Создано: {card.created_at}\n\n"
                      + f"{LEVEL_TO_COLOR[repetition.level]}({LEVEL_TO_PERCENT[repetition.level]}) - 🕓 {repetition.next_review_date}"
                      for card in pagination.get_current_page_items()
                  ) + menu_text)

        inl_markup = pagination.update_kb_repetition_detail(repetition.id, current_page_cards[0].id)

        await callback_query.message.edit_text(result, reply_markup=inl_markup)
    else:
        await callback_query.message.edit_text("Детали повторения не найдены.")

    await callback_query.answer()

async def on_approve_repetition(callback_query: CallbackQuery, session_maker: sessionmaker):
    data_parts = callback_query.data.split('_')
    repetition_id = int(data_parts[2])
    current_page = int(data_parts[3])  # Извлекаем номер страницы
    await update_repetition(session_maker, repetition_id, success=True)
    await callback_query.answer("Отлично! Карточка успешно повторена.", show_alert=False)

    await on_details_repetition_pagination(callback_query, session_maker, current_page)


async def on_decline_repetition(callback_query: CallbackQuery, session_maker: sessionmaker):
    data_parts = callback_query.data.split('_')
    repetition_id = int(data_parts[2])
    current_page = int(data_parts[3])  # Извлекаем номер страницы
    await update_repetition(session_maker, repetition_id, success=False)
    await callback_query.answer("Ничего страшного, попробуйте ещё раз!", show_alert=False)

    await on_details_repetition_pagination(callback_query, session_maker, current_page)
