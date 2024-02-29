# Создаём фильтр для данных колбэка пагинации
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from redis.asyncio import Redis
from sqlalchemy.orm import sessionmaker

from core.db import get_all_user_cards, get_user_cards_by_word, get_repetitions_by_card_id, LEVEL_TO_PERCENT, \
    get_user_page_size_dictionary
from core.handlers.utils import format_word, menu_text
from core.keyboards import MAIN_MENU_BOARD
from .paginations import Pagination
from ..structures.fsm_group import GetCardState


async def on_start(message: Message, session_maker: sessionmaker, redis: Redis):
    user_id = message.from_user.id
    user_cards = await get_all_user_cards(session_maker, user_id)
    page_size = await get_user_page_size_dictionary(user_id, session_maker, redis)
    pagination = Pagination(user_cards, page_size=page_size)
    cards_list = "\n".join(f"▫️ {card.foreign_word} - <tg-spoiler>{card.translation}</tg-spoiler>"
                           for card in pagination.get_current_page_items())

    dictionary_content = (f"📖 Словарь:\n\nДля работы с конкретной карточкой используйте команду /get_card"
                          f"\n\n{cards_list}" + menu_text)

    await message.answer(dictionary_content,
                         reply_markup=pagination.update_kb_general())


async def on_pagination(callback_query: CallbackQuery, session_maker: sessionmaker, redis: Redis):
    page_action, page_number = callback_query.data.split('_')[1], callback_query.data.split('_')[2]
    page_number = int(page_number)

    user_id = callback_query.from_user.id
    user_cards = await get_all_user_cards(session_maker, user_id)
    page_size = await get_user_page_size_dictionary(user_id, session_maker, redis)

    pagination = Pagination(user_cards, page_size=page_size)
    pagination.current_page = page_number

    if page_action == "page":
        cards_list = "\n".join(f"▫️ {card.foreign_word} - <tg-spoiler>{card.translation}</tg-spoiler>"
                               for card in pagination.get_current_page_items())

        dictionary_content = (f"📖 Словарь:\n\nДля работы с конкретной карточкой используйте команду /get_card"
                              f"\n\n{cards_list}" + menu_text)

        await callback_query.message.edit_text(dictionary_content,
                                               reply_markup=pagination.update_kb_general())
        await callback_query.answer()


async def on_get_card_details(message: Message, state: FSMContext, session_maker: sessionmaker):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Пожалуйста введите слово для поиска:")
        await state.set_state(GetCardState.waiting_for_word)
        # return
    else:
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
                f"Процент: {LEVEL_TO_PERCENT[repetition.level]}, Следующий повтор: {repetition.next_review_date}"
                for repetition in repetitions_info
            )

            response += f"Повторения:\n{repetition_details}" + menu_text

            inl_markup = pagination.update_kb_detail(detail_word=word, card_id=current_page_cards[0].id)

            await message.answer(response, reply_markup=inl_markup)
        else:
            await message.answer("Не найдена карточка(и) с данным словом.", reply_markup=MAIN_MENU_BOARD)


async def on_word_received(message: Message, state: FSMContext, session_maker: sessionmaker):
    word = format_word(message.text)
    user_id = message.from_user.id
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
            f"Процент: {LEVEL_TO_PERCENT[repetition.level]}, Следующий повтор: {repetition.next_review_date}"
            for repetition in repetitions_info
        )

        response += f"Повторения:\n{repetition_details}" + menu_text

        inl_markup = pagination.update_kb_detail(detail_word=word, card_id=current_page_cards[0].id)
        await message.answer(response, reply_markup=inl_markup)
    else:
        await message.answer("Не найдена карточка(и) с данным словом.", reply_markup=MAIN_MENU_BOARD)

    # Ваш код для обработки найденных карточек...

    # После обработки сбрасываем состояние
    await state.clear()


async def on_card_details_pagination(callback_query: CallbackQuery, session_maker: sessionmaker):
    data_parts = callback_query.data.split('_')
    # Мы ожидаем, что data_parts будет содержать как минимум 3 элемента: ['cards','details', 'Music', 'page', '2',]
    if len(data_parts) < 5 or not data_parts[4].isdigit():
        await callback_query.answer("Ошибка: неправильный формат данных пагинации.")
        return

    action, word, page_action, page_number = data_parts[1], data_parts[2], data_parts[3], int(data_parts[4]),

    user_id = callback_query.from_user.id
    cards = await get_user_cards_by_word(session_maker, user_id, word)

    if cards:
        pagination = Pagination(cards, page_size=1)
        pagination.current_page = page_number
        current_page_cards = pagination.get_current_page_items()

        response = f"№{page_number} {word}:\n\n" + "\n".join(
            f"Слово: {card.foreign_word}\n"
            f"Перевод: {card.translation}\n"
            + (f"Транскрипция: {card.transcription}\n" if card.transcription else "")
            + (f"Контекст: {card.example_usage}\n" if card.example_usage else "")
            + f"Создано: {card.created_at}\n\n"
            for card in pagination.get_current_page_items()
        )

        repetitions_info = await get_repetitions_by_card_id(session_maker, current_page_cards[0].id)
        repetition_details = '\n'.join(
            f"Процент: {LEVEL_TO_PERCENT[repetition.level]}, Следующий повтор: {repetition.next_review_date}"
            for repetition in repetitions_info
        )

        response += f"Повторения:\n{repetition_details}\n\n" + menu_text

        inl_markup = pagination.update_kb_detail(detail_word=word, card_id=current_page_cards[0].id)

        await callback_query.message.edit_text(response, reply_markup=inl_markup)
        await callback_query.answer()
    else:
        await callback_query.answer("Карточка(и) с таким словом не найдены.")
