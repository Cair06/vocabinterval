from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker
from aiogram.types import Message
from core.handlers.start import get_start
from aiogram.types import ReplyKeyboardRemove
from core.db import create_card
from core.structures.fsm_group import CardStates


async def update_card_creation_message(bot_message_id, instruction_message_id, state, message, **kwargs):
    card_info = await state.get_data()
    card_info.update(kwargs)
    
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=(
            'Создайте новую карточку!📝\n'
            '<i>Если у вас имеются несколько слов/предложений в одном из разделов разделите их запятыми</i>\n\n'
            f'Слово: {card_info.get("card_foreign_word", "🚫")}' + (" ✅" if card_info.get("card_foreign_word") is not None else "") + '\n'
            f'Перевод: {card_info.get("card_translation", "🚫")}' + (" ✅" if card_info.get("card_translation") is not None else "") + '\n'
            f'Транскрипция: {card_info.get("card_transcription", "🚫")}' + (" ✅" if card_info.get("card_transcription") is not None else "") + '\n'
            f'Контекст: {card_info.get("card_example_usage", "🚫")}' + (" ✅" if card_info.get("card_example_usage") is not None else "")
            )
    )
    # Редактируем сообщение с инструкцией на следующий шаг
    next_step = card_info.get("next_step")
    if next_step:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=instruction_message_id,
            text=next_step
        )
    # Обновляем данные состояния
    await state.update_data(**card_info)


def format_word(word):
    return word.lower().capitalize()