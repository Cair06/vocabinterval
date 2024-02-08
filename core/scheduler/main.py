from datetime import datetime

from aiogram import Bot
from aiogram.client import bot

from arq import cron
from arq.connections import RedisSettings

from core.settings import settings, postgres_url, redis_settings
from core.db import get_user_ids_with_repetitions_for_today, create_async_engine, get_session_maker
from core.keyboards.main_menu import MAIN_MENU_BOARD


async_engine = create_async_engine(postgres_url)
session_maker = get_session_maker(async_engine)

bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")


async def send_daily_reminders(ctx):
    async with session_maker() as session:
        today = datetime.utcnow().date()
        user_ids_to_notify = await get_user_ids_with_repetitions_for_today(session, today)
        message = ("🧩 У вас есть слова для повторения! \n\nДля более подробной информации, посмотрите список "
                   "повторений.")

        for user_id in user_ids_to_notify:
            await bot.send_message(chat_id=user_id, text=message, reply_markup=MAIN_MENU_BOARD)


class WorkerSettings:
    functions = [send_daily_reminders, ]
    redis_settings = RedisSettings(**redis_settings)
    cron_jobs = [
        cron(
            send_daily_reminders,
            name="send-daily-reminders",
            hour=17,  # запуск в 20:00 по МСК(UTC +3)
            minute=0
        ), ]
        # cron(
        #     send_daily_reminders,
        #     name="send-daily-reminders",
        #     second=0,  # Запуск каждую минуту для тестирования
        # )]
