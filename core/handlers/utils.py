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


async def display_repetition_details(callback_query, session_maker, repetition_id, pagination):
    repetition = await session_maker.get(Repetition, repetition_id)

    details = f"Слово: {repetition.card.foreign_word}\nУровень: {LEVEL_TO_COLOR[repetition.level]}({repetition.level})\nСледующий повтор: {repetition.next_review_date}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить ✅", callback_data=f"approve_{repetition_id}"),
         InlineKeyboardButton(text="Отложить ❌", callback_data=f"postpone_{repetition_id}")],
        pagination.create_navigation_buttons(f"repetition_nav_{repetition.card_id}")
    ])

    await callback_query.message.edit_text(details, reply_markup=keyboard)
