# Создаём фильтр для данных колбэка пагинации
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker
from core.structures.fsm_group import DeleteCardState
from core.db import delete_card, delete_all_user_cards
from core.keyboards.cancel_board import CANCEL_AND_NEXT_BOARD
from core.keyboards import MAIN_MENU_BOARD


async def on_delete_all_cards(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Вы действительно хотите удалить все карточки?",
                                        reply_markup=CANCEL_AND_NEXT_BOARD)
    await state.set_state(DeleteCardState.waiting_for_confirm_delete_all)


async def on_delete_all_cards_confirm(message: Message, session_maker: sessionmaker, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer("Удаление всех карточек отменено.", reply_markup=MAIN_MENU_BOARD)
        await state.clear()
    elif message.text == "Продолжить":
        user_id = message.from_user.id
        # Функция для удаления всех карточек пользователя (необходимо реализовать)
        await delete_all_user_cards(session_maker, user_id)
        await message.answer("Все карточки удалены.", reply_markup=MAIN_MENU_BOARD)
        await state.clear()


async def on_delete_card(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(card_id=callback_query.data.split('_')[-1])  # Сохраняем ID карточки в состояние
    await callback_query.message.answer("Вы действительно хотите удалить эту карточку?",
                                        reply_markup=CANCEL_AND_NEXT_BOARD)

    await state.set_state(DeleteCardState.waiting_for_confirm_delete)


async def on_delete_card_confirm(message: Message, session_maker: sessionmaker, state: FSMContext):
    user_data = await state.get_data()
    card_id = int(user_data.get('card_id'))

    if message.text == 'Отмена':
        await state.clear()
        await message.answer("Удаление отменено.", reply_markup=MAIN_MENU_BOARD)
    elif message.text == "Продолжить":
        deleted = await delete_card(session_maker, card_id, message.from_user.id)
        if deleted:
            await message.answer("Карточка удалена.", reply_markup=MAIN_MENU_BOARD)
        else:
            await message.answer("Ошибка удаления карточки.", reply_markup=MAIN_MENU_BOARD)
        await state.clear()
