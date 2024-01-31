import datetime

from redis.asyncio.client import Redis
from sqlalchemy import Column, BigInteger, VARCHAR, DATE, select
from sqlalchemy.orm import relationship, sessionmaker, selectinload
from sqlalchemy.exc import ProgrammingError


from .base import BaseModel


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
    async with session_maker() as session:
        async with session.begin():
            user = User(
                user_id=user_id,
                username=username
            )
            try:
                session.add(user)
            except ProgrammingError as e:
                # TODO: add log
                pass


async def is_user_exists(user_id: int, session_maker: sessionmaker, redis: Redis) -> bool:
    res = await redis.get(name='is_user_exists:' + str(user_id))
    if not res:
        async with session_maker() as session:
            async with session.begin():
                sql_res = await session.execute(select(User).where(User.user_id == user_id))
                await redis.set(name='is_user_exists:' + str(user_id), value=1 if sql_res else 0)
                return bool(sql_res)
    else:
        return bool(res)