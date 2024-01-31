from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Pagination:
    def __init__(self, items, page_size=10):
        self.items = items
        self.page_size = page_size
        self.total_pages = max(1, len(items) // page_size + (1 if len(items) % page_size else 0))
        self.current_page = 1

    def get_current_page_items(self):
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end]

    # Для всех карточек(словарь)
    def update_kb_general(self):
        navigation_buttons = []
        action_buttons = []
        base_callback_data = "page"

        if self.current_page > 1:
            navigation_buttons.append(
                InlineKeyboardButton(text="⬅️", callback_data=f"{base_callback_data}_{self.current_page - 1}"))

        navigation_buttons.append(
            InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))

        if self.current_page < self.total_pages:
            navigation_buttons.append(
                InlineKeyboardButton(text="➡️", callback_data=f"{base_callback_data}_{self.current_page + 1}"))

        action_buttons.append(InlineKeyboardButton(text="🗑️ Удалить все карточки", callback_data="delete_all_cards"))

        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, action_buttons])

    # Для конкретнной карточки
    def update_kb_detail(self, detail_word, card_id=None):
        navigation_buttons = []
        action_buttons = []
        base_callback_data = "details_page"

        if self.current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️",
                                                           callback_data=f"{base_callback_data}_{self.current_page - 1}_{detail_word}"))

        navigation_buttons.append(
            InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))

        if self.current_page < self.total_pages:
            navigation_buttons.append(InlineKeyboardButton(text="➡️",
                                                           callback_data=f"{base_callback_data}_{self.current_page + 1}_{detail_word}"))

        # Если указан card_id, добавляем кнопки Редактировать и Удалить
        if card_id is not None:
            action_buttons.append(InlineKeyboardButton(text="✏️", callback_data=f"edit_card_{card_id}"))
            action_buttons.append(InlineKeyboardButton(text="🗑️", callback_data=f"delete_card_{card_id}"))

        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, action_buttons])

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
