from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    save = relationship("PlayerSave", back_populates="user", uselist=False)


class PlayerSave(Base):
    __tablename__ = "player_saves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    save_data = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="save")