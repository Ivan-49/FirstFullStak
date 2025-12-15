from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserOut(BaseModel):
    id: int
    name: str
    username: str

class FileOut(BaseModel):
    id: int
    filename: str
    filepath: str
    size_bytes: Optional[int]

class LessonOut(BaseModel):
    id: int
    lesson_number: int
    subject: str
    teacher: str
    room: str
    files: List[FileOut]

class ScheduleOut(BaseModel):
    date: str
    notes: Optional[str]
    lessons: List[LessonOut]
