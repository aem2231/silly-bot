from sqlalchemy import Column, Integer, String, Float
from db.database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    level = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    last_daily = Column(Integer, default=0)
    last_work = Column(Integer, default=0)
