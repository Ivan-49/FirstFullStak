from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
import os

class Base(DeclarativeBase):  # ✅ Base сразу!
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
sessionmaker = None

@asynccontextmanager
async def lifespan(app):
    global engine, sessionmaker
    print("🚀 STARTUP: Создаём asyncpg engine...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ✅ Теперь Base существует!
        print("✅ ТАБЛИЦЫ СОЗДАНЫ!")
    
    yield
    
    print("🔌 SHUTDOWN...")
    await engine.dispose()

async def get_db():
    if sessionmaker is None:
        raise Exception("Database not initialized!")
    async with sessionmaker() as session:
        yield session
