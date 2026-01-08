"""
Database Connection

This module handles the database engine creation and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.core.config import DATABASE_URL

# Create the SQLAlchemy engine. 
# check_same_thread=False is needed for SQLite, remove for Postgres/MySQL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a customized Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: The SQLAlchemy database session.
        
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

