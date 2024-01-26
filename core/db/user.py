import datetime

from sqlalchemy import Column, BigInteger, VARCHAR, DATE
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
    
    
    def __str__(self) -> str:
        return f"--User:{self.user_id}--"