# backend/app/core/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Use your env var, or default to a local sqlite file under app/data/
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/data/wazfini.db")

# SQLite needs this flag; for Postgres/MySQL it’s ignored
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Sync SQLAlchemy engine (matches your main.py usage)
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

# Classic sync Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for your ORM models
Base = declarative_base()

# Dependency used by FastAPI routes to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
