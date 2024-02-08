from aiogram import types
from sqlalchemy import func, desc
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from core.db import Card, User
from core.settings import settings


async def get_top_users_by_cards(session_maker: sessionmaker, limit: int = 10):
    async with session_maker() as session:
        query = (
            select(
                User.user_id.label('user_id'),
                User.username,
                func.count(Card.id).label('cards_count')
            )
            .join(User, User.user_id == Card.user_id)  # Присоединяем таблицу пользователей
            .group_by(User.user_id, User.username)
            .order_by(desc('cards_count'))
            .limit(limit)
        )
        result = await session.execute(query)
        return result.all()


# Обработчик команды для просмотра топ пользователей
async def top_users(message: types.Message, session_maker: sessionmaker):
    if message.from_user.id == settings.bots.admin_id:
        top_users = await get_top_users_by_cards(session_maker)
        response_message = "❤️‍🔥 Топ пользователей по количеству карточек:\n\n"
        for user_id, username, cards_count in top_users:
            display_name = f"🔸@{username}" if username else f"🔹ID {user_id}"
            response_message += f"{display_name}: {cards_count} 📄\n"
        await message.answer(response_message)
    else:
        await message.answer("У вас нет доступа к этой команде.")
