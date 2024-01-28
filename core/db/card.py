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
    desc
)
from sqlalchemy.orm import relationship, sessionmaker, Session, selectinload
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseModel


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

    repetitions = relationship("Repetition", back_populates="card")
    
    
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
    Создать пост
    :param foreign_word:
    :param translation:
    :param session_maker:
    :param transcription:
    :param example_usage:
    :param user_id:
    :param budget:
    :param pub_price:
    :param url_price:
    :return:
    """
    async with session_maker() as session:
        async with session.begin():
            card = Card(
                foreign_word=foreign_word,
                translation = translation,
                transcription = transcription,
                example_usage = example_usage,
                user_id = user_id,
            )
            session: AsyncSession | Session
            try:
                session.add(card)
            except ProgrammingError as e:
                logging.error(e)
                return None
            else:
                return card
            
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
