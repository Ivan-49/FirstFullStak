from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import app.database as database

Base = database.Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True)
    password_hash = Column(String(64))  # ✅ ДОБАВЬ!
    files = relationship("File", back_populates="user")

class ScheduleDate(Base):
    __tablename__ = "schedule_dates"
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    notes = Column(String(500))
    lessons = relationship("Lesson", back_populates="schedule_date")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    date_id = Column(Integer, ForeignKey("schedule_dates.id"))
    lesson_number = Column(Integer, nullable=False)
    subject = Column(String(100))
    teacher = Column(String(100))
    room = Column(String(20))
    schedule_date = relationship("ScheduleDate", back_populates="lessons")  # ✅ ДОБАВЛЕНО!
    files = relationship("File", back_populates="lesson")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    size_bytes = Column(BigInteger)
    uploaded_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="files")
    lesson = relationship("Lesson", back_populates="files")  # ✅ ИСПРАВЛЕНО!
