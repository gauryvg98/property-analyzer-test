from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./real_estate.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def fetch_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_tables():
    # drop and create again on every restart (quick hacky way to ensure we dont overload data)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
