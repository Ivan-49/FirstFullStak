from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
import re
from . import database, models, auth, crud

from fastapi.responses import FileResponse
import os



app = FastAPI(title="Расписание ВГУ", lifespan=database.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_db() -> AsyncSession:
    async with database.sessionmaker() as session:
        yield session

def parse_date(date_str: str) -> date:
    """Парсит ЛЮБОЙ формат: DD.MM.YYYY, YYYY-MM-DD, YYYY.MM.DD"""
    date_str = date_str.strip()
    
    # YYYY-MM-DD (ISO)
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        pass
    
    # DD.MM.YYYY
    match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
    if match:
        day, month, year = map(int, match.groups())
        return date(year, month, day)
    
    # YYYY.MM.DD
    match = re.match(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_str)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)
    
    raise HTTPException(400, f"Неверный формат даты: '{date_str}'. Используй DD.MM.YYYY, YYYY-MM-DD или YYYY.MM.DD")

@app.get("/")
async def root():
    return {"message": "Backend работает! 🚀 /docs для Swagger"}

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await crud.create_user(db, username, password, name)
        return {"message": "Пользователь создан", "user_id": user.id}
    except Exception as e:
        raise HTTPException(400, f"Ошибка регистрации: {str(e)}")

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await crud.authenticate_user(db, username, password)
        token = auth.create_token(user.id)
        return {
            "token": token, 
            "user": {"id": user.id, "name": user.name, "username": user.username}
        }
    except Exception:
        raise HTTPException(401, "Неверные данные")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    lesson_id: int = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_id = auth.verify_token(credentials.credentials)
        db_file = await crud.create_file(db, user_id, lesson_id, file)
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "filepath": db_file.filepath,
            "size": db_file.size_bytes,
            "message": "Файл загружен!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")

@app.get("/schedule/{date_str}")
async def get_schedule(
    date_str: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    auth.verify_token(credentials.credentials)
    target_date = parse_date(date_str)
    
    # Найди/создай дату
    stmt = select(models.ScheduleDate).where(models.ScheduleDate.date == target_date)
    result = await db.execute(stmt)
    schedule_date = result.scalar_one_or_none()
    
    if not schedule_date:
        schedule_date = models.ScheduleDate(date=target_date)
        db.add(schedule_date)
        await db.commit()
        await db.refresh(schedule_date)
    
    # Получи уроки
    lessons = await crud.get_lessons_by_date(db, schedule_date.id)
    
    return {
        "date": target_date.isoformat(),
        "notes": getattr(schedule_date, 'notes', '') or "",
        "lessons": [
            {
                "id": l.id,
                "lesson_number": l.lesson_number,
                "subject": getattr(l, 'subject', '') or "",
                "teacher": getattr(l, 'teacher', '') or "",
                "room": getattr(l, 'room', '') or "",
                "files": []
            } for l in lessons
        ]
    }

@app.get("/files/{file_id}")
async def get_file_info(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    auth.verify_token(credentials.credentials)
    file = await crud.get_file(db, file_id)
    if not file:
        raise HTTPException(404, "Файл не найден")
    return {
        "id": file.id,
        "filename": file.filename,
        "filepath": file.filepath,
        "size": file.size_bytes,
        "download_url": f"/static/{file.filename}"
    }

@app.get("/dates")
async def get_dates(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    auth.verify_token(credentials.credentials)
    dates = await crud.get_recent_dates(db)
    return [{"date": d.date.isoformat(), "notes": d.notes or ""} for d in dates]




@app.get("/files/download/{file_id}")
async def download_file(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Скачать файл"""
    try:
        user_id = auth.verify_token(credentials.credentials)
    except:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    # Получаем файл
    file = await crud.get_file(db, file_id)
    if not file or file.user_id != user_id:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Правильный путь
    filename = os.path.basename(file.filepath)  # "2025-03-19_18-33-13.png"
    file_path = f"/app/uploads/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл отсутствует на диске")
    
    # FileResponse с ASCII именем
    return FileResponse(
        path=file_path,
        filename="file.png",  # Без кириллицы!
        media_type='application/octet-stream',
        headers={"Content-Disposition": 'attachment; filename="file.png"'}
    )



@app.post("/schedule/{date_str}")
async def create_or_get_schedule(
    date_str: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Создать/получить расписание с 8 пустыми парами"""
    auth.verify_token(credentials.credentials)
    target_date = parse_date(date_str)
    
    # Найти/создать дату
    stmt = select(models.ScheduleDate).where(models.ScheduleDate.date == target_date)
    result = await db.execute(stmt)
    schedule_date = result.scalar_one_or_none()
    
    if not schedule_date:
        schedule_date = models.ScheduleDate(date=target_date, notes="")
        db.add(schedule_date)
        await db.commit()
        await db.refresh(schedule_date)
    
    # Создать 8 стандартных пар если пусто
    lessons_count = (await db.execute(
        select(models.Lesson).where(models.Lesson.date_id == schedule_date.id)
    )).scalars().all()
    
    if not lessons_count:
        for i in range(1, 9):
            lesson = models.Lesson(
                date_id=schedule_date.id,
                lesson_number=i,
                subject=f"Пара {i}",
                teacher="",
                room=""
            )
            db.add(lesson)
        await db.commit()
    
    lessons = await crud.get_lessons_by_date(db, schedule_date.id)
    
    return {
        "date": target_date.isoformat(),
        "notes": schedule_date.notes or "",
        "lessons": [
            {
                "id": l.id,
                "lesson_number": l.lesson_number,
                "subject": l.subject or "",
                "teacher": l.teacher or "",
                "room": l.room or "",
                "files": [f.id for f in await crud.get_lesson_files(db, l.id)]
            } for l in lessons
        ]
    }

@app.post("/lessons/{lesson_id}/files")
async def upload_lesson_file(
    lesson_id: int,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Загрузить файл К КОНКРЕТНОЙ ПАРЕ"""
    user_id = auth.verify_token(credentials.credentials)
    lesson = await crud.get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(404, "Пара не найдена")
    
    db_file = await crud.create_file(db, user_id, lesson_id, file)
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "lesson_id": lesson_id,
        "message": "Файл прикреплён к паре!"
    }

@app.put("/lessons/{lesson_id}")
async def update_lesson_info(
    lesson_id: int,
    subject: str = Form(None),
    teacher: str = Form(None),
    room: str = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Обновить информацию о паре"""
    auth.verify_token(credentials.credentials)
    lesson = await crud.update_lesson(db, lesson_id, subject, teacher, room)
    return {
        "id": lesson.id,
        "lesson_number": lesson.lesson_number,
        "subject": lesson.subject,
        "teacher": lesson.teacher,
        "room": lesson.room
    }
@app.get("/files/download/{file_id}")
async def download_file(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Скачать файл (доступно всем авторизованным!)"""
    auth.verify_token(credentials.credentials)  # Только проверка токена
    
    file = await crud.get_file(db, file_id)
    if not file:
        raise HTTPException(404, "Файл не найден")
    
    filename = os.path.basename(file.filepath)
    file_path = f"/app/uploads/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "Файл отсутствует")
    
    return FileResponse(
        path=file_path,
        filename="file.png",
        media_type='application/octet-stream',
        headers={"Content-Disposition": 'attachment; filename="file.png"'}
    )

@app.delete("/files/{file_id}")
async def delete_file_endpoint(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Удалить файл"""
    auth.verify_token(credentials.credentials)
    try:
        result = await crud.delete_file(db, file_id)
        return result
    except ValueError:
        raise HTTPException(404, "Файл не найден")

@app.delete("/lessons/{lesson_id}")
async def delete_lesson_endpoint(
    lesson_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Удалить пару + ВСЕ файлы"""
    auth.verify_token(credentials.credentials)
    try:
        result = await crud.delete_lesson(db, lesson_id)
        return result
    except ValueError:
        raise HTTPException(404, "Пара не найдена")
