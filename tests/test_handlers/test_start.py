from unittest.mock import AsyncMock
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.handlers.start import get_start
from tests.utils import TEST_USER, TEST_USER_CHAT


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await get_start(message)

    # Проверяем, что метод answer был вызван хотя бы один раз
    assert message.answer.called
    # Получаем аргументы последнего вызова
    args, kwargs = message.answer.call_args
    # Проверяем текст сообщения
    assert args[0] == "Меню"
    # Проверяем наличие кнопок в клавиатуре
    keyboard = kwargs['reply_markup'].keyboard
    assert len(keyboard) > 0  # Проверяем, что клавиатура не пустая
    # Проверяем текст на кнопках
    expected_buttons = ["Помощь", "Словарь", "Добавить карточку"]
    for row in keyboard:
        for button in row:
            assert button.text in expected_buttons


@pytest.mark.asyncio
def callback_handler(storage, bot):
    call = AsyncMock()
    state = FSMContext(
        bot=bot,
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id)
    )

   # await "SHALABIBI SHALABU"