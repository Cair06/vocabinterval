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

    def create_navigation_buttons(self, callback_data_prefix):
        navigation_buttons = []
        if self.current_page > 1:
            navigation_buttons.append(
                InlineKeyboardButton(text="⬅️", callback_data=f"{callback_data_prefix}_{self.current_page - 1}"))
        navigation_buttons.append(
            InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))
        if self.current_page < self.total_pages:
            navigation_buttons.append(
                InlineKeyboardButton(text="➡️", callback_data=f"{callback_data_prefix}_{self.current_page + 1}"))
        return navigation_buttons

    def update_kb_general(self):
        navigation_buttons = self.create_navigation_buttons("cards_page")
        action_buttons = [InlineKeyboardButton(text="🗑️ Удалить все карточки", callback_data="delete_all_cards")]
        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, action_buttons])

    def update_kb_detail(self, detail_word, card_id):
        navigation_buttons = self.create_navigation_buttons(f"cards_details_{detail_word}_page")
        action_buttons = [
            InlineKeyboardButton(text="✏️", callback_data=f"edit_card_{card_id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"delete_card_{card_id}")
        ]
        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, action_buttons])

    def update_kb_repetitions(self):
        navigation_buttons = self.create_navigation_buttons("repetitions_page")
        action_buttons = [InlineKeyboardButton(text="🔄 Повторить", callback_data=f"detail_repetition"),]
        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, action_buttons])

    def update_kb_repetition_detail(self, repetition_id, card_id):
        navigation_buttons = self.create_navigation_buttons("repetition_detail_page")
        translation = [InlineKeyboardButton(text="Показать перевод", callback_data=f"show_translation_{card_id}"),]

        action_buttons = [
            InlineKeyboardButton(text="❌", callback_data=f"decline_repetition_{repetition_id}"),
            InlineKeyboardButton(text="✅", callback_data=f"approve_repetition_{repetition_id}"),
        ]
        return InlineKeyboardMarkup(inline_keyboard=[navigation_buttons, translation, action_buttons])


    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
