import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import sessionmaker, Session
from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:domKing@localhost/fastapi"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True:
    try:
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', port = 5432, user = 'postgres',
                            password = 'domKing', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as Error:
        print("Connecting to database failed!")
        print("Error: ", Error)
        time.sleep(2)
