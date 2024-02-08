# Создаём фильтр для данных колбэка пагинации
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from aiogram.fsm.context import FSMContext

from core.structures.fsm_group import EditCardState
from core.db import update_card
from core.keyboards import CHOOSE_FIELD_TO_EDIT, MAIN_MENU_BOARD
from .utils import menu_text
from .get_cards import on_get_card_details


async def on_edit_card(callback_query: CallbackQuery, session_maker: sessionmaker, state: FSMContext):
    """
    :param
    """
    _, __, card_id = callback_query.data.split('_')
    card_id = int(card_id)

    # Сохраняем card_id во временное хранилище состояний
    await state.update_data(card_id=card_id)
    await callback_query.message.answer("Выберите поле для редактирования:" + menu_text,
                                        reply_markup=CHOOSE_FIELD_TO_EDIT)
    await state.set_state(EditCardState.waiting_for_field_choice)
    await callback_query.answer()


async def on_field_choice(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик выбора поля для редактирования"""
    field = callback_query.data.split('_')[2]
    # Сохраняем выбранное поле во временное хранилище состояний
    await state.update_data(field_to_edit=field)
    await callback_query.message.answer(f"Введите новое значение для поля {field}:")
    
    await state.set_state(EditCardState.waiting_for_field_value)
    await callback_query.answer()
    

async def on_field_value(message: Message, session_maker: sessionmaker, state: FSMContext):
    """Обработчик ввода нового значения поля"""
    new_value = message.text
    user_data = await state.get_data()
    card_id = user_data['card_id']
    field_to_edit = user_data['field_to_edit']
    word = user_data.get('word')

    # Обновляем карточку с новым значением
    field_to_update = {field_to_edit: new_value}
    updated = await update_card(session_maker, card_id, message.from_user.id, **field_to_update)
    
    if updated:
        await message.answer("Карточка успешно обновлена.", reply_markup=MAIN_MENU_BOARD)        
        await on_get_card_details(message, session_maker, word)
    else:
        await message.answer("Ошибка при обновлении карточки.", reply_markup=MAIN_MENU_BOARD)

    await state.clear()
