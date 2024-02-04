# from typing import Callable, Dict, Any, Awaitable
#
# from aiogram import BaseMiddleware
# from aiogram.types import Message, CallbackQuery
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import select
#
# from db import User
#
#
# class RegisterCheck(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#         event: Message|CallbackQuery,
#         data: Dict[str, Any]
#     ) -> Any:
#
#         session_maker: sessionmaker = data["session_maker"]
#         async with session_maker() as session:
#             async with session.begin():
#                 result = await session.execute(select(User).where(User.user_id == event.from_user.id))
#                 user: User = result.one_or_none()
#
#                 if user is not None:
#                     pass
#                 else:
#                     user = User(
#                         user_id = event.from_user.id,
#                         username = event.from_user.username
#                     )
#
#                     await session.merge(user)
#                     if isinstance(event, Message):
#                         await event.answer("Вы успешно зарегистрированы!")
#                     else:
#                         await event.message.answer("Вы успешно зарегистрированы!")
#
#         return await handler(event, data)


#  Copyright (c) 2022.

from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from core.db import is_user_exists, create_user
import logging

logger = logging.getLogger(__name__)


class RegisterCheck(BaseMiddleware):
    """
    Middleware будет вызываться каждый раз, когда пользователь будет отправлять боту сообщения (или нажимать
    на кнопку в инлайн-клавиатуре).
    """

    def __init__(self):
        """
        Не нужен в нашем случае
        """
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """ Сама функция для обработки вызова """
        # if event.web_app_data:
        #     return await handler(event, data)

        session_maker = data['session_maker']
        redis = data['redis']
        user = event.from_user
        logger.info(f"User {event.from_user.id} in register CHECK ALOOOOOOOOOOOOOOOOOOOOOOO")

        # Получаем менеджер сессий из ключевых аргументов, переданных в start_polling()
        if not await is_user_exists(user_id=event.from_user.id, session_maker=session_maker, redis=redis):

            await create_user(user_id=event.from_user.id,
                              username=event.from_user.username, session_maker=session_maker)
            await data['bot'].send_message(event.from_user.id, 'Ты успешно зарегистрирован(а)!')

        return await handler(event, data)