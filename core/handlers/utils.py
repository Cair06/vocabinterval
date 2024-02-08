async def update_card_creation_message(bot_message_id, instruction_message_id, state, message, **kwargs):
    card_info = await state.get_data()
    card_info.update(kwargs)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=(
                'Создайте новую карточку!📝\n'
                '<i>Если у вас имеются несколько слов/предложений в одном из разделов разделите их запятыми</i>\n\n'
                f'Слово: {card_info.get("card_foreign_word", "🚫")}' + (
                    " ✅" if card_info.get("card_foreign_word") is not None else "") + '\n'
                                                                                      f'Перевод: {card_info.get("card_translation", "🚫")}' + (
                    " ✅" if card_info.get("card_translation") is not None else "") + '\n'
                                                                                     f'Транскрипция: {card_info.get("card_transcription", "🚫")}' + (
                    " ✅" if card_info.get("card_transcription") is not None else "") + '\n'
                                                                                       f'Контекст: {card_info.get("card_example_usage", "🚫")}' + (
                    " ✅" if card_info.get("card_example_usage") is not None else "")
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
    await state.update_data(**card_info)


def format_word(word):
    return word.lower().capitalize()


START_SPEECH = (
    "Привет! Добро пожаловать в нашего учебного помощника по изучению слов. Вот что я могу для вас сделать:\n\n"
    "🔍 Помощь и Инструкции - Нажмите /help для общей информации о доступных командах. "
    "Если нужна помощь по конкретной команде, введите /help сразу же после команды, и я предоставлю вам детальное "
    "описание.\n\n"
    "📚 Карточки - Вы можете использовать: создание, чтение, изменение, удаление для операций над карточками."
    " Моя база данных содержит все слова, которые вы изучаете. \n\n"
    "⏰ Напоминания о Повторении - Я буду напоминать вам о необходимости повторения слов через 1, 3, 7, 21, 60, 180, "
    "и 360 дней в 20:00 по МСК (UTC+3), чтобы обеспечить лучшее усвоение материала.\n"
)

menu_text = "\n\nНажмите на /menu, чтобы вернуться к меню."
