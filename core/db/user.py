import datetime

from redis.asyncio.client import Redis
from sqlalchemy import Column, BigInteger, VARCHAR, DATE, select, text, Integer
from sqlalchemy.orm import relationship, sessionmaker, selectinload
from sqlalchemy.exc import ProgrammingError

from .base import BaseModel
import logging

logger = logging.getLogger(__name__)


class User(BaseModel):
    __tablename__ = "users"

    # Telegram user id
    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)

    # Telegram user name
    username = Column(VARCHAR(32), unique=False, nullable=True)

    # Registration date
    reg_date = Column(DATE, default=datetime.date.today())

    # Last update date
    upd_date = Column(DATE, default=datetime.date.today())

    # Отношение между пользователем и его карточками
    cards = relationship("Card", back_populates="user")

    page_size_dictionary = Column(Integer, default=10)  # Значение по умолчанию 10

    def __str__(self) -> str:
        return f"--User:{self.user_id}--"


async def get_user(user_id: int, session_maker: sessionmaker) -> User:
    """
    Получить пользователя по его id
    :param user_id:
    :param session_maker:
    :return:
    """
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(User)
                .options(selectinload(User.cards))
                .filter(User.user_id == user_id)  # type: ignore
            )
            return result.scalars().one()


async def create_user(user_id: int, username: str, session_maker: sessionmaker) -> None:
    logger.info(f"In create_user")
    async with session_maker() as session:
        async with session.begin():
            user = User(
                user_id=user_id,
                username=username
            )
            try:
                session.add(user)
                await session.commit()
            except ProgrammingError as e:
                logger.error(f"Error creating user: {e}")
                raise


async def is_user_exists(user_id: int, session_maker: sessionmaker, redis: Redis) -> bool:
    res = 0 if await redis.get(name='is_user_exists:' + str(user_id)) is None else 1
    if not res:
        async with session_maker() as session:
            async with session.begin():
                sql_res = await session.execute(select(User).where(User.user_id == user_id))
                user = sql_res.scalars().first()
                await redis.set(name='is_user_exists:' + str(user_id),
                                value='1' if user is not None else '0')
                return user is not None
    else:
        return bool(int(res))


async def get_user_page_size_dictionary(user_id: int, session_maker: sessionmaker, redis: Redis) -> int:
    # Сначала пытаемся получить размер страницы из Redis
    page_size = await redis.get(name=f'user:{user_id}:page_size_dictionary')

    if page_size is None:  # Если в Redis нет информации
        async with session_maker() as session:
            async with session.begin():
                # Извлекаем информацию из базы данных
                user = await session.get(User, user_id)
                if user:
                    page_size = user.page_size_dictionary
                    # Кешируем полученный размер страницы в Redis на определенное время, например, на 1 день (86400 секунд)
                    await redis.set(name=f'user:{user_id}:page_size', value=str(page_size))
                else:
                    # Если пользователя нет в базе данных, используем размер страницы по умолчанию
                    page_size = 10  # Задаем размер страницы по умолчанию
                    await redis.set(name=f'user:{user_id}:page_size', value=str(page_size))
    else:
        page_size = int(page_size)  # Преобразуем значение из Redis в целое число

    return int(page_size)


async def update_user_page_size_dictionary(user_id: int, new_size: int, session_maker: sessionmaker,
                                           redis: Redis) -> bool:
    """
    Обновляет размер страницы словаря для пользователя и кеширует его в Redis.
    :param user_id: ID пользователя.
    :param new_size: Новый размер страницы.
    :param session_maker: Фабрика сессий для подключения к БД.
    :param redis: Клиент Redis.
    :return: True, если обновление прошло успешно, иначе False.
    """
    async with session_maker() as session:
        async with session.begin():
            # Обновляем размер страницы в базе данных
            user = await session.get(User, user_id)
            if user:
                user.page_size_dictionary = new_size  # Предполагаем, что у модели пользователя есть такое поле
                await session.commit()

                # Кешируем новый размер страницы в Redis
                await redis.set(name=f'user:{user_id}:page_size_dictionary', value=str(new_size))
                return True
            return False
