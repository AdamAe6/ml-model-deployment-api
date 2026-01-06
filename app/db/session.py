from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.create_db import engine

DATABASE_URL = "postgresql://adamakeb@localhost:5432/ml_api_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """
    Fournit une session de base de données SQLAlchemy pour les dépendances FastAPI.

    Returns
    -------
    Generator[Session, None, None]
        Générateur qui yield une session DB et s'assure de la fermer après usage.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
