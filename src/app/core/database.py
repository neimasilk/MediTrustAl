from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_CONFIG

# Create SQLAlchemy engine
engine = create_engine(DATABASE_CONFIG["url"])

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 