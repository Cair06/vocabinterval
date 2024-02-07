from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandStart

from .start import (
    get_start,
    help_command,
    help_func,
    noop_callback_handler, menu_command
)

from .create_card import (
    menu_card_create_confirmation,
    menu_card_create,
    menu_card_create_word,
    menu_card_create_translate,
    menu_card_create_transcription,
    menu_posts_create_example_usage
)
from .get_cards import (
    on_start,
    on_pagination,
    on_get_card_details,
    on_card_details_pagination
)

from .edit_card import (
    on_edit_card,
    on_field_choice,
    on_field_value
)

from .delete_card import (
    on_delete_card,
    on_delete_card_confirm,
    on_delete_all_cards,
    on_delete_all_cards_confirm
)

from .get_cards_repetition import (
    on_repetition_cards_start,
    on_repetition_cards_pagination,
)

from .edit_repetition import (
    on_details_repetition,
    on_approve_repetition,
    on_decline_repetition,
    on_details_repetition_pagination
)

from core.structures.fsm_group import CardStates, EditCardState, DeleteCardState
from .paginations import Pagination

__all__ = ["register_user_commands", "get_start", "Pagination"]


def register_user_commands(router: Router) -> None:
    """
    Зарегистрировать хендлеры пользователя
    :param router:
    """
    # Основные
    router.message.register(get_start, CommandStart())
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(menu_command, Command(commands=['menu']))
    router.message.register(get_start, F.text == 'Старт')
    router.message.register(help_func, F.text == "Помощь")
    router.message.register(on_start, F.text == 'Словарь')

    # Добавление карточек
    router.message.register(menu_card_create_confirmation, F.text == 'Добавить карточку')
    router.message.register(menu_card_create, CardStates.waiting_for_confirmation)
    router.message.register(menu_card_create_word, CardStates.waiting_for_word)
    router.message.register(menu_card_create_translate, CardStates.waiting_for_translation)
    router.message.register(menu_card_create_transcription, CardStates.waiting_for_transcription)
    router.message.register(menu_posts_create_example_usage, CardStates.waiting_for_example_usage)

    # Навигация в словаре
    router.callback_query.register(on_pagination, lambda c: c.data.startswith('cards_page_'))

    # Данные об определенной карточке
    router.message.register(on_get_card_details, Command(commands=['get_card']))
    router.callback_query.register(on_card_details_pagination, lambda c: c.data.startswith('cards_details_'))

    # Для изменения определенной карточки
    router.callback_query.register(on_edit_card, lambda c: c.data.startswith('edit_card_'))
    router.callback_query.register(on_field_choice, lambda c: c.data.startswith('card_edit_'))
    router.message.register(on_field_value, EditCardState.waiting_for_field_value)

    # Удаление карточки(ек)
    router.callback_query.register(on_delete_all_cards, lambda c: c.data == 'delete_all_cards')
    router.message.register(on_delete_all_cards_confirm, DeleteCardState.waiting_for_confirm_delete_all)
    router.callback_query.register(on_delete_card, lambda c: c.data.startswith('delete_card_'))
    router.message.register(on_delete_card_confirm, DeleteCardState.waiting_for_confirm_delete)

    router.message.register(on_repetition_cards_start, F.text == 'Список повторений')
    router.callback_query.register(on_repetition_cards_pagination, lambda c: c.data.startswith('repetitions_page_'))

    router.callback_query.register(on_details_repetition, lambda c: c.data == 'detail_repetition')
    router.callback_query.register(on_approve_repetition, lambda c: c.data.startswith('approve_repetition_'))
    router.callback_query.register(on_decline_repetition, lambda c: c.data.startswith('decline_repetition_'))
    router.callback_query.register(on_details_repetition_pagination, lambda c: c.data.startswith('repetition_detail_page'))

    # no operation
    router.callback_query.register(noop_callback_handler, lambda c: c.data == 'noop')


# Alias
register_user_handlers = register_user_commands
