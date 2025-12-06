from datetime import datetime
import os

from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from sqlalchemy import create_engine, DateTime, text
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PSWD = os.getenv("DB_PSWD")
DB_SCHEMA = os.getenv("DB_SCHEMA")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PSWD}@{DB_HOST}:{DB_PORT}/{DB_SCHEMA}"

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_POOL_MAX_OVERFLOW", "20")),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TIME_ZONE_QUERY = "now() AT TIME ZONE 'Asia/Seoul'"


class TimeStampModel:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text(f"({TIME_ZONE_QUERY})"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 server_default=text(f"({TIME_ZONE_QUERY})"),
                                                 onupdate=text(f"({TIME_ZONE_QUERY})"))
