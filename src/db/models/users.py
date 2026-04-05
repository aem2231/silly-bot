from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    balance = Column(Integer, default=0)
    last_daily = Column(Integer, default=0)
    last_work = Column(Integer, default=0)
