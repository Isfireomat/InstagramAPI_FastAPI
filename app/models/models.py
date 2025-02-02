from sqlalchemy import Column, String, ForeignKey, DateTime,BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), nullable=False)

class Message(Base):
    __tablename__ = 'Message'
    id = Column(BigInteger, primary_key=True)
    text = Column(String(1024), nullable=False)
    sender_id = Column(BigInteger, ForeignKey('User.id'), nullable=False)
    recipient_id = Column(BigInteger, ForeignKey('User.id'), nullable=False)
    created_time = Column(DateTime, default=func.now(), nullable=False)