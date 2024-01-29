# Создаём фильтр для данных колбэка пагинации
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker
from core.structures.fsm_group import DeleteCardState
from core.db import delete_card
from core.keyboards.cancel_board import CANCEL_AND_NEXT_BOARD


async def on_delete_card(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(card_id=callback_query.data.split('_')[-1])  # Сохраняем ID карточки в состояние
    await callback_query.message.answer("Вы действительно хотите удалить эту карточку?", reply_markup=CANCEL_AND_NEXT_BOARD)

    await state.set_state(DeleteCardState.waiting_for_confirm_delete)


async def on_delete_card_confirm(message: Message, session_maker: sessionmaker, state: FSMContext):
    user_data = await state.get_data()
    card_id = int(user_data.get('card_id'))

    if message.text == 'Отмена':
        await message.answer("Удаление отменено.", reply_markup=ReplyKeyboardRemove())
        await state.clear()  # Очищаем состояние
    elif message.text == "Продолжить":
        deleted = await delete_card(session_maker, card_id, message.from_user.id)
        if deleted:
            await message.answer("Карточка удалена.", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Ошибка удаления карточки.", reply_markup=ReplyKeyboardRemove())
        await state.clear()