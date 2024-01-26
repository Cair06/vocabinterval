from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from core.db import User


class RegisterCheck(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message|CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:

        session_maker: sessionmaker = data["session_maker"]
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(select(User).where(User.user_id == event.from_user.id))
                user: User = result.one_or_none()
                
                if user is not None:
                    pass
                else:
                    user = User(
                        user_id = event.from_user.id,
                        username = event.from_user.username
                    )
                    
                    await session.merge(user)
                    if isinstance(event, Message):
                        await event.answer("Вы успешно зарегистрированы!")
                    else:
                        await event.message.answer("Вы успешно зарегистрированы!")
                
        return await handler(event, data)