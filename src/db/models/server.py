from sqlalchemy import Column, Integer, String
from db.database import Base

class Server(Base):
    __tablename__ = 'server'
    guild_id = Column(String, primary_key=True)
    last_bank_rob = Column(Integer, default=0)
