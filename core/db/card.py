import datetime
import logging

from sqlalchemy import (
    Column,
    BigInteger,
    VARCHAR,
    DATE,
    ForeignKey,
    SmallInteger,
    CheckConstraint,
    select,
    desc,
    delete
)
from sqlalchemy.orm import relationship, sessionmaker, Session, selectinload
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseModel

REVIEW_INTERVALS = {
    1: datetime.timedelta(days=1),
    2: datetime.timedelta(days=3),
    3: datetime.timedelta(days=7),
    4: datetime.timedelta(days=21),
    5: datetime.timedelta(days=60),
    6: datetime.timedelta(days=180),
    7: datetime.timedelta(days=360),
}

LEVEL_TO_COLOR = {
    0: "⚫️",
    1: "🟤",
    2: "🔴",
    3: "🟠",
    4: "🟡",
    5: "🟢",
    6: "🔵",
    7: "🟣",
}


LEVEL_TO_PERCENT = {
    0: "0%",
    1: "15%",
    2: "30%",
    3: "45%",
    4: "60%",
    5: "75%",
    6: "90%",
    7: "100%",
}

class Card(BaseModel):
    __tablename__ = "cards"

    id = Column(BigInteger, primary_key=True, index=True)
    foreign_word = Column(VARCHAR(255), index=True)
    translation = Column(VARCHAR(255), nullable=False)
    transcription = Column(VARCHAR(255))
    example_usage = Column(VARCHAR(512))
    created_at = Column(DATE, default=datetime.date.today())

    # Ссылка на пользователя
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="cards")

    repetitions = relationship("Repetition", back_populates="card", cascade="all, delete")

    
    def __str__(self) -> str:
        return f"--Card: {self.foreign_word}--"


class Repetition(BaseModel):
    __tablename__ = "repetitions"

    id = Column(BigInteger, primary_key=True, index=True)
    card_id = Column(BigInteger, ForeignKey("cards.id"))
    level = Column(SmallInteger, nullable=False, default=0)
    next_review_date = Column(DATE)

    card = relationship("Card", back_populates="repetitions")
    
    __table_args__ = (
        CheckConstraint("level >= 0 AND level <= 7", name="check_level_range"),
    )
    def __str__(self) -> str:
        return f"--Repetition: ID:{self.card_id} Word:{self.card.foreign_word} Next review date: {self.next_review_date}--"


async def create_card(
        session_maker: sessionmaker,
        foreign_word: str,
        translation: str,
        transcription: str,
        example_usage: str,
        user_id: BigInteger,
) -> Card | None:
    """
    Создать карточку и связанное повторение.
    :param foreign_word:
    :param translation:
    :param session_maker:
    :param transcription:
    :param example_usage:
    :param user_id:
    :return: Созданная карточка или None
    """
    async with session_maker() as session:
        async with session.begin():
            # Создаем карточку
            card = Card(
                foreign_word=foreign_word,
                translation=translation,
                transcription=transcription,
                example_usage=example_usage,
                user_id=user_id,
            )
            session.add(card)
            await session.flush()  # Обновляем идентификаторы для только что созданных объектов

            # Создаем связанное повторение
            repetition = Repetition(
                card=card, 
                level=0,
                next_review_date=datetime.date.today()
            )
            session.add(repetition)
            try:
                await session.commit()
                return card
            except ProgrammingError as e:
                logging.error(e)
                await session.rollback()
                return None

   
async def get_all_user_cards(session_maker: sessionmaker, user_id: BigInteger) -> list[Card]:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(Card).filter(Card.user_id == user_id).order_by(desc(Card.created_at)))
            return result.scalars().all()
        
        
async def get_user_cards_by_word(session_maker: sessionmaker, user_id: BigInteger, word: str) -> list[Card]:
    async with session_maker() as session:
        async with session.begin():
            # Добавляем фильтр по foreign_word в запрос
            result = await session.execute(
                select(Card)
                .filter(Card.user_id == user_id, Card.foreign_word == word)
                .order_by(desc(Card.created_at))
            )
            return result.scalars().all()


async def delete_card(session_maker: sessionmaker, card_id: int, user_id: BigInteger) -> bool:
    async with session_maker() as session:
        async with session.begin():
            card_to_delete = await session.get(Card, card_id)
            if card_to_delete and card_to_delete.user_id == user_id:
                await session.delete(card_to_delete)
                return True
            return False


async def update_card(session_maker: sessionmaker, card_id: int, user_id: BigInteger, **kwargs) -> bool:
    async with session_maker() as session:
        async with session.begin():
            card_to_update = await session.get(Card, card_id)
            if card_to_update and card_to_update.user_id == user_id:
                for attr, value in kwargs.items():
                    setattr(card_to_update, attr, value)
                session.add(card_to_update)
                return True
            return False
        
        
async def delete_all_user_cards(session_maker: sessionmaker, user_id: int) -> None:
    """
    Удаляет все карточки пользователя из базы данных.
    :param session_maker: Фабрика сессий для подключения к БД.
    :param user_id: Идентификатор пользователя.
    """
    async with session_maker() as session:
        async with session.begin():
            # Удаляем все карточки, принадлежащие пользователю
            await session.execute(
                delete(Card)
                .where(Card.user_id == user_id)
            )
            await session.commit()



async def get_repetitions_by_card_id(session_maker: sessionmaker, card_id: int) -> list[Repetition]:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Repetition)
                .where(Repetition.card_id == card_id)
                .order_by(Repetition.next_review_date)
            )
            return result.scalars().all()
        

async def update_repetition(session_maker: sessionmaker, repetition_id: int, success: bool) -> None:
    async with session_maker() as session:
        async with session.begin():
            repetition = await session.get(Repetition, repetition_id)
            if repetition and success:
                repetition.level = min(repetition.level + 1, 7)  # Предотвращаем уровень выше максимального
                interval = REVIEW_INTERVALS.get(repetition.level, datetime.timedelta(days=1))
                repetition.next_review_date = datetime.date.today() + interval
                session.add(repetition)
            await session.commit()


async def get_cards_for_repetition(session_maker: sessionmaker, user_id: BigInteger, date: datetime.date) -> list[Card]:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Card)
                .join(Repetition, Repetition.card_id == Card.id)
                .filter(Card.user_id == user_id, Repetition.next_review_date <= date)
                .order_by(Repetition.next_review_date)
            )
            return result.scalars().all()
