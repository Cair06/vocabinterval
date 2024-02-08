from aiogram.fsm.state import StatesGroup, State


class CardStates(StatesGroup):
    """
        Состояния для постов
    """
    waiting_for_confirmation = State()
    waiting_for_word = State()
    waiting_for_translation = State()
    waiting_for_example_usage = State()
    waiting_for_transcription = State()


class EditCardState(StatesGroup):
    waiting_for_field_choice = State()
    waiting_for_field_value = State()


class GetCardState(StatesGroup):
    waiting_for_word = State()

class DeleteCardState(StatesGroup):
    waiting_for_confirm_delete = State()
    waiting_for_confirm_delete_all = State()
