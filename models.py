from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base   # ✅ THIS LINE WAS MISSING


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    settings = relationship("UserSettings", back_populates="user", uselist=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    groq_api_key = Column(String, nullable=True)
    resume_text = Column(String, nullable=True)

    user = relationship("User", back_populates="settings")
