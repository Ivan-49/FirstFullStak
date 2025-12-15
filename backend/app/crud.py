from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from passlib.context import CryptContext
import hashlib
import os
from datetime import datetime

# ✅ Поддержка bcrypt + старых SHA256
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, username: str, name: str, password: str):
    """Создать пользователя"""
    # Проверяем существование
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Пользователь уже существует")
    
    # ✅ bcrypt (обрезаем >72 байт)
    if len(password.encode()) > 72:
        password = password[:72]
    
    password_hash = pwd_context.hash(password)
    
    user = models.User(
        username=username,
        name=name,
        password_hash=password_hash
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Аутентификация (SHA256 + bcrypt)"""
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError("Пользователь не найден")
    
    # ✅ SHA256 для СТАРЫХ пользователей (6dfd2040...)
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.password_hash == sha256_hash:
        return user
    
    # ✅ bcrypt для НОВЫХ пользователей
    if pwd_context.verify(password, user.password_hash):
        return user
    
    raise ValueError("Неверный пароль")

async def create_file(db: AsyncSession, user_id: int, lesson_id: int, file: 'UploadFile'):
    """Загрузить файл"""
    # Создаём папку uploads
    os.makedirs("/app/uploads", exist_ok=True)
    
    # Уникальное имя файла
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = f"uploads/{filename}"
    full_path = f"/app/uploads/{filename}"
    
    # Сохраняем файл
    content = await file.read()
    with open(full_path, "wb") as buffer:
        buffer.write(content)
    
    # Сохраняем в БД
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
    """Получить файл по ID"""
    stmt = select(models.File).where(models.File.id == file_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_lessons_by_date(db: AsyncSession, date_id: int):
    """Получить уроки по дате"""
    stmt = select(models.Lesson).where(models.Lesson.date_id == date_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_recent_dates(db: AsyncSession, limit: int = 30):
    """Последние даты расписания"""
    stmt = select(models.ScheduleDate).order_by(models.ScheduleDate.date.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_lesson_files(db: AsyncSession, lesson_id: int):
    """Файлы конкретной пары"""
    stmt = select(models.File).where(models.File.lesson_id == lesson_id).order_by(models.File.uploaded_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_lesson(db: AsyncSession, date_id: int, lesson_number: int, subject: str = "", teacher: str = "", room: str = ""):
    """Создать пару"""
    lesson = models.Lesson(
        date_id=date_id,
        lesson_number=lesson_number,
        subject=subject,
        teacher=teacher,
        room=room
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson
async def get_lesson(db: AsyncSession, lesson_id: int):
    """Получить пару"""
    stmt = select(models.Lesson).where(models.Lesson.id == lesson_id)
    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise ValueError(f"Пара с id={lesson_id} не найдена")
    return lesson

async def update_lesson(db: AsyncSession, lesson_id: int, subject: str = None, teacher: str = None, room: str = None):
    """Обновить пару"""
    lesson = await get_lesson(db, lesson_id)  # ✅ Теперь НЕ None!
    
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
    """Удалить файл + с диска"""
    file = await get_file(db, file_id)
    if not file:
        raise ValueError("Файл не найден")
    
    # Удаляем с диска
    full_path = f"/app/uploads/{os.path.basename(file.filepath)}"
    if os.path.exists(full_path):
        os.remove(full_path)
    
    # Удаляем из БД
    await db.delete(file)
    await db.commit()
    return {"message": "Файл удалён"}

async def delete_lesson(db: AsyncSession, lesson_id: int):
    """Удалить пару + ВСЕ её файлы"""
    lesson = await get_lesson(db, lesson_id)
    if not lesson:
        raise ValueError("Пара не найдена")
    
    # Удаляем все файлы пары
    files = await get_lesson_files(db, lesson_id)
    for file in files:
        full_path = f"/app/uploads/{os.path.basename(file.filepath)}"
        if os.path.exists(full_path):
            os.remove(full_path)
        await db.delete(file)
    
    # Удаляем пару
    await db.delete(lesson)
    await db.commit()
    return {"message": "Пара и файлы удалены"}
