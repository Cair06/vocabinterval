# Создаём фильтр для данных колбэка пагинации
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker

from db import get_all_user_cards, get_user_cards_by_word, get_repetitions_by_card_id
from .paginations import Pagination
from handlers.utils import format_word
from keyboards import MAIN_MENU_BOARD


async def on_start(message: Message, session_maker: sessionmaker):
    user_id = message.from_user.id
    user_cards = await get_all_user_cards(session_maker, user_id)
    pagination = Pagination(user_cards, page_size=10)
    cards_list = "\n".join(f"▫️ {card.foreign_word}" for card in pagination.get_current_page_items())

    await message.answer(f"📖 Словарь:\n\n{cards_list}",
                         reply_markup=pagination.update_kb_general())


async def on_pagination(callback_query: CallbackQuery, session_maker: sessionmaker):
    page_action, page_number = callback_query.data.split('_')
    page_number = int(page_number)
    
    user_id = callback_query.from_user.id
    user_cards = await get_all_user_cards(session_maker, user_id)
    pagination = Pagination(user_cards, page_size=10)
    pagination.current_page = page_number
    
    if page_action == "page":
        cards_list = "\n".join(f"▫️ {card.foreign_word}" for card in pagination.get_current_page_items())
        await callback_query.message.edit_text(f"📖 Словарь:\n\n{cards_list}", reply_markup=pagination.update_kb_general())
        await callback_query.answer()


async def on_get_card_details(message: Message, session_maker: sessionmaker):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Пожалуйства введите слово для поиска.")
        return

    word = format_word(args[1])
    cards = await get_user_cards_by_word(session_maker, user_id, word)

    if cards:
        pagination = Pagination(cards, page_size=1)  
        current_page_cards = pagination.get_current_page_items()

        response = f"№1 {word}:\n\n" + '\n'.join(
            f"Слово: {card.foreign_word}\n"
            f"Перевод: {card.translation}\n"
            + (f"Транскрипция: {card.transcription}\n" if card.transcription else "")
            + (f"Контекст: {card.example_usage}\n" if card.example_usage else "")
            + f"Создано: {card.created_at}\n\n"
            for card in current_page_cards
        )
        
        repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
        repetition_details = '\n'.join(
            f"Уровень: {repetition.level}, Следующий повтор: {repetition.next_review_date}"
            for repetition in repetitions_info
        )

        response += f"Повторения:\n{repetition_details}"
        await message.answer(response, reply_markup=pagination.update_kb_detail(detail_word=word,
                                                                                card_id=current_page_cards[0].id))
    else:
        await message.answer("Не найдена карточка(и) с данным словом.", reply_markup=MAIN_MENU_BOARD)

        
async def on_card_details_pagination(callback_query: CallbackQuery, session_maker: sessionmaker):
    data_parts = callback_query.data.split('_')
    # Мы ожидаем, что data_parts будет содержать как минимум 3 элемента: ['details', 'page', '2', 'Music']
    if len(data_parts) < 4 or not data_parts[2].isdigit():
        await callback_query.answer("Ошибка: неправильный формат данных пагинации.")
        return

    action, page_action, page_number, word = data_parts[0], data_parts[1], int(data_parts[2]), data_parts[3]

    user_id = callback_query.from_user.id
    cards = await get_user_cards_by_word(session_maker, user_id, word)

    if cards:
        pagination = Pagination(cards, page_size=1)
        pagination.current_page = page_number
        current_page_cards = pagination.get_current_page_items()

        cards_details = f"№{page_number} {word}:\n\n" + "\n".join(
            f"Слово: {card.foreign_word}\n"
            f"Перевод: {card.translation}\n"
            + (f"Транскрипция: {card.transcription}\n" if card.transcription else "")
            + (f"Контекст: {card.example_usage}\n" if card.example_usage else "")
            + f"Создано: {card.created_at}\n\n"
            for card in pagination.get_current_page_items()
        )
        await callback_query.message.edit_text(cards_details,
                                               reply_markup=pagination.update_kb_detail(detail_word=word,
                                                                                        card_id=current_page_cards[0].id))
        await callback_query.answer()
    else:
        await callback_query.answer("Карточка(и) с таким словом не найдены.")