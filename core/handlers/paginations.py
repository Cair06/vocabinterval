from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery



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


    # def update_kb(self, detail_word=False):
    #     buttons = []
        
    #     #Если хендлер вызывает для словаря:page Если из конкретного слова: details_page
    #     page_type = "page" if detail_word else "details_page" 

    #     # Добавляем кнопку "Назад", если это возможно
    #     if self.current_page > 1:
    #         buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{page_type}_{self.current_page - 1}"))

    #     # Добавляем кнопку с текущей страницей
    #     buttons.append(InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="current_page"))

    #     # Добавляем кнопку "Вперед", если это возможно
    #     if self.current_page < self.total_pages:
    #         buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"{page_type}_{self.current_page + 1}"))

    #     keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    #     return keyboard
    
    # def update_kb(self, detail_word=None):
    #     buttons = []
    #     base_callback_data = "details_page" if detail_word else "page"

    #     # Добавляем кнопку "Назад", если это возможно
    #     if self.current_page > 1:
    #         callback_data = f"{base_callback_data}_{self.current_page - 1}"
    #         if detail_word:
    #             callback_data += f"_{detail_word}"
    #         buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))

    #     # Добавляем кнопку с текущей страницей
    #     buttons.append(InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))

    #     # Добавляем кнопку "Вперед", если это возможно
    #     if self.current_page < self.total_pages:
    #         callback_data = f"{base_callback_data}_{self.current_page + 1}"
    #         if detail_word:
    #             callback_data += f"_{detail_word}"
    #         buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=callback_data))

    #     keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    #     return keyboard

    # Для всех карточек(словарь)
    def update_kb_general(self):
        buttons = []
        base_callback_data = "page"

        # Добавляем кнопку "Назад", если это возможно
        if self.current_page > 1:
            buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{base_callback_data}_{self.current_page - 1}"))

        # Добавляем кнопку с текущей страницей
        buttons.append(InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))

        # Добавляем кнопку "Вперед", если это возможно
        if self.current_page < self.total_pages:
            buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"{base_callback_data}_{self.current_page + 1}"))

        return InlineKeyboardMarkup(inline_keyboard=[buttons])

    # Для конкретнной карточки
    def update_kb_detail(self, detail_word, card_id=None):
        buttons = []
        base_callback_data = "details_page"

        # Добавляем кнопку "Назад", если это возможно
        if self.current_page > 1:
            buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{base_callback_data}_{self.current_page - 1}_{detail_word}"))

        buttons.append(InlineKeyboardButton(text=f"{self.current_page}/{self.total_pages}", callback_data="noop"))

        # Добавляем кнопку "Вперед", если это возможно
        if self.current_page < self.total_pages:
            buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"{base_callback_data}_{self.current_page + 1}_{detail_word}"))

        # Если указан card_id, добавляем кнопки Редактировать и Удалить
        if card_id is not None:
            buttons.append(InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_card_{card_id}"))
            buttons.append(InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_card_{card_id}"))

        return InlineKeyboardMarkup(inline_keyboard=[buttons])



    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1