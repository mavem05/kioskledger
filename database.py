import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Fetch the database URL from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the database session in our API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()