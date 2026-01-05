from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.create_db import engine

DATABASE_URL = "postgresql://adamakeb@localhost:5432/ml_api_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
