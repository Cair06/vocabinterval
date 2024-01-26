import datetime

from sqlalchemy import Column, BigInteger, VARCHAR, DATE, ForeignKey, SmallInteger, CheckConstraint
from sqlalchemy.orm import relationship
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
