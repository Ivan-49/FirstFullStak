print("🚨 LOADED CORRECT CRUDE.PY!!!")
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from fastapi import UploadFile  # ✅ Фикс импорта
import hashlib
import os
from datetime import datetime


async def create_user(db: AsyncSession, username: str, name: str, password: str):
    """Создать пользователя - ЧИСТЫЙ SHA256"""
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Пользователь уже существует")
    
    # 🔥 ОДИНАКОВЫЙ SHA256 ДЛЯ ВСЕГО
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    user = models.User(username=username, name=name, password_hash=password_hash)
    print(f"🔥 CREATE DEBUG: '{password}' -> '{password_hash}'")

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Аутентификация - ТОТ ЖЕ SHA256"""
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError("Пользователь не найден")
    
    # 🔥 ТОТ ЖЕ SHA256
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    print(f"🔥 LOGIN DEBUG: DB='{user.password_hash[:10]}...', INPUT='{sha256_hash[:10]}...'")
    if user.password_hash == sha256_hash:

        return user
    
    raise ValueError("Неверный пароль")


async def create_file(db: AsyncSession, user_id: int, lesson_id: int, file: UploadFile):
    """Загрузить файл"""
    os.makedirs("/app/uploads", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = f"uploads/{filename}"
    full_path = f"/app/uploads/{filename}"
    
    content = await file.read()
    with open(full_path, "wb") as buffer:
        buffer.write(content)
    
    db_file = models.File(
        user_id=user_id,
        lesson_id=lesson_id,
        filename=file.filename,
        filepath=filepath,
        size_bytes=len(content)
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file


async def get_file(db: AsyncSession, file_id: int):
    stmt = select(models.File).where(models.File.id == file_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_lessons_by_date(db: AsyncSession, date_id: int):
    stmt = select(models.Lesson).where(models.Lesson.date_id == date_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_recent_dates(db: AsyncSession, limit: int = 30):
    stmt = select(models.ScheduleDate).order_by(models.ScheduleDate.date.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_lesson_files(db: AsyncSession, lesson_id: int):
    stmt = select(models.File).where(models.File.lesson_id == lesson_id).order_by(models.File.uploaded_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_lesson(db: AsyncSession, date_id: int, lesson_number: int, subject: str = "", teacher: str = "", room: str = ""):

        
    lesson = models.Lesson(
        date_id=int(date_id),
        lesson_number=int(lesson_number),
        subject=subject,
        teacher=teacher,
        room=room
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def get_lesson(db: AsyncSession, lesson_id: int):
    stmt = select(models.Lesson).where(models.Lesson.id == lesson_id)
    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise ValueError(f"Пара с id={lesson_id} не найдена")
    return lesson


async def update_lesson(db: AsyncSession, lesson_id: int, subject: str = None, teacher: str = None, room: str = None):
    lesson = await get_lesson(db, lesson_id)
    
    if subject is not None:
        lesson.subject = subject
    if teacher is not None:
        lesson.teacher = teacher
    if room is not None:
        lesson.room = room
    
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def delete_file(db: AsyncSession, file_id: int):
    file = await get_file(db, file_id)
    if not file:
        raise ValueError("Файл не найден")
    
    full_path = f"/app/{file.filepath}"
    if os.path.exists(full_path):
        os.remove(full_path)
    
    await db.delete(file)
    await db.commit()
    return {"message": "Файл удалён"}


async def delete_lesson(db: AsyncSession, lesson_id: int):
    lesson = await get_lesson(db, lesson_id)
    
    files = await get_lesson_files(db, lesson_id)
    for file in files:
        full_path = f"/app/{file.filepath}"
        if os.path.exists(full_path):
            os.remove(full_path)
        await db.delete(file)
    
    await db.delete(lesson)
    await db.commit()
    return {"message": "Пара и файлы удалены"}

    