from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from sqlalchemy.orm import sessionmaker

from core.handlers.utils import update_card_creation_message, format_word
from core.structures.fsm_group import CardStates
from core.keyboards import CANCEL_BOARD,  CANCEL_AND_NEXT_BOARD, MAIN_MENU_BOARD
from core.db import create_card



async def menu_card_create_confirmation(message: types.Message, state: FSMContext):
    await message.answer("Если вы готовы начать добавление карточки нажмите 'Продолжить' ", reply_markup=CANCEL_AND_NEXT_BOARD)
    await state.set_state(CardStates.waiting_for_confirmation)



async def menu_card_create(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.clear()
        return await message.answer("Создание карточки отменено.", reply_markup=MAIN_MENU_BOARD)
    elif message.text == "Продолжить":
        bot_message = await message.answer('Создайте новую карточку!📝\n<i>Если у вас имеются несколько слов/предложений в одном из разделов разделите их запятыми</i>\n\nСлово: 🚫\nПеревод: 🚫\nТранскрипция: 🚫\nКонтекст: 🚫')
        await state.update_data(bot_message_id=bot_message.message_id)
        instruction_message = await message.answer('Введите слово:')
        await state.update_data(instruction_message_id=instruction_message.message_id)
        await state.set_state(CardStates.waiting_for_word)


async def menu_card_create_word(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.clear()
        return await message.answer("Создание карточки отменено.", reply_markup=MAIN_MENU_BOARD)
    user_data = await state.get_data()
    await update_card_creation_message(
        bot_message_id=user_data['bot_message_id'],
        instruction_message_id=user_data['instruction_message_id'],
        state=state,
        message=message,
        card_foreign_word=message.text,
        next_step="Введите перевод:",
        reply_markup=CANCEL_AND_NEXT_BOARD

    )
    await state.set_state(CardStates.waiting_for_translation)


async def menu_card_create_translate(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    bot_message_id = user_data['bot_message_id']
    instruction_message_id = user_data['instruction_message_id']

    # Проверяем ввод пользователя
    if message.text == 'Отмена':
        await state.clear()
        return await message.answer("Создание карточки отменено.", reply_markup=MAIN_MENU_BOARD)
    elif message.text == "Продолжить":
        card_translation = ""
        await message.answer("Поле 'Перевод' обязательное. Пожалуйста, введите перевод.")
        return 

    else:
        card_translation = message.text

    # Обновляем сообщения
    await update_card_creation_message(
        bot_message_id=bot_message_id,
        instruction_message_id=instruction_message_id,
        state=state,
        message=message,
        card_translation=card_translation,
        next_step="Введите транскрипцию (или отправьте 'Продолжить', если её нет):",
        reply_markup=CANCEL_BOARD
    )

    # Устанавливаем следующее состояние
    await state.set_state(CardStates.waiting_for_transcription)


async def menu_card_create_transcription(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    bot_message_id = user_data['bot_message_id']
    instruction_message_id = user_data['instruction_message_id']

    # Проверяем ввод пользователя
    if message.text == 'Отмена':
        await state.clear()
        return await message.answer("Создание карточки отменено.", reply_markup=MAIN_MENU_BOARD)
    elif message.text == "Продолжить":
        card_transcription = ""
    else:
        card_transcription = message.text

    # Обновляем сообщения
    await update_card_creation_message(
        bot_message_id=bot_message_id,
        instruction_message_id=instruction_message_id,
        state=state,
        message=message,
        card_transcription=card_transcription,
        next_step="Введите пример использования (или отправьте 'Продолжить', если его нет):",
        reply_markup=CANCEL_AND_NEXT_BOARD
    )

    # Устанавливаем следующее состояние
    await state.set_state(CardStates.waiting_for_example_usage)


async def menu_posts_create_example_usage(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    user_data = await state.get_data()
    bot_message_id = user_data['bot_message_id']
    instruction_message_id = user_data['instruction_message_id']

    # Проверяем ввод пользователя
    if message.text == 'Отмена':
        await state.clear()
        return await message.answer("Создание карточки отменено.", reply_markup=MAIN_MENU_BOARD)
    elif message.text == "Продолжить":
        card_example_usage = ""
    else:
        card_example_usage = message.text

    # Обновляем сообщения
    await update_card_creation_message(
        bot_message_id=bot_message_id,
        instruction_message_id=instruction_message_id,
        state=state,
        message=message,
        card_example_usage=card_example_usage,
        next_step=None,  # Нет следующего шага, так как это последний
        reply_markup=CANCEL_AND_NEXT_BOARD
    )

    # Создаем карточку в базе данных
    card_foreign_word = format_word(user_data['card_foreign_word']) if user_data['card_foreign_word'] != "" else None
    card_translation = format_word(user_data['card_translation']) if user_data['card_translation'] != "" else None
    card_transcription = format_word(user_data['card_transcription']) if user_data['card_transcription'] != "" else None
    card_example_usage = format_word(card_example_usage) if card_example_usage != "" else None
    card = await create_card(
        session_maker=session_maker,
        foreign_word=card_foreign_word,
        translation=card_translation,
        transcription=card_transcription,
        example_usage=card_example_usage,
        user_id=message.from_user.id,
    )

    # Отправляем сообщение о создании карточки
    if card:
        await message.answer("Карта была успешно создана!", reply_markup=MAIN_MENU_BOARD)
    else:
        await message.answer("Произошла ошибка при создании карточки.", reply_markup=MAIN_MENU_BOARD)

    # Очищаем состояние
    await state.clear()
    # Удаляем сообщение с инструкцией
    await message.bot.delete_message(chat_id=message.chat.id, message_id=instruction_message_id)