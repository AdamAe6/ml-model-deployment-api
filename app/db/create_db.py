from sqlalchemy import create_engine
from app.db.models import Base

DATABASE_URL = "postgresql://adamakeb@localhost:5432/ml_api_db"

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
