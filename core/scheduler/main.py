import asyncio

from aiogram import Bot
from aiogram.client import bot
from arq import create_pool, cron
from datetime import datetime, timedelta

from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, create_session, selectinload

from core.settings import settings,  postgres_url, redis_settings
from core.db import Card, Repetition
from core.db.engine import create_async_engine, get_session_maker

async_engine = create_async_engine(postgres_url)
session_maker = get_session_maker(async_engine)

bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")


async def send_daily_reminders(ctx):
    async with session_maker() as session:
        today = datetime.utcnow().date()
        query = select(Repetition).where(Repetition.next_review_date == today).options(selectinload(Repetition.card))
        result = await session.execute(query)
        cards_to_review = result.scalars().all()

        for repetition in cards_to_review:
            card: Card = repetition.card
            user_id = card.user_id
            message = f"Пора повторить слово: {card.foreign_word}"
            await bot.send_message(chat_id=user_id, text=message)  # функция bot.send_message должна быть асинхронной


class WorkerSettings:
    functions = [send_daily_reminders, ]
    redis_settings = RedisSettings(**redis_settings)
    cron_jobs = [
        cron(
            send_daily_reminders,
            name="send-daily-reminders",
            hour=0,  # запуск в полночь по UTC
            minute=0
        ),]
    #     cron(
    #         send_daily_reminders,
    #         name="send-daily-reminders",
    #         second=0,  # Запуск каждую минуту для тестирования
    #     )
    # ]

#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(create_pool(RedisSettings(**redis_settings)))
