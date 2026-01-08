"""
User Model

This module defines the database schema for Users of the application.
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class User(Base):
    """
    SQLAlchemy model representing a User.

    Attributes:
        id (int): Primary key.
        github_id (int): Unique ID from GitHub.
        github_username (str): GitHub username.
        github_email (str): Email address from GitHub (if available).
        github_access_token (str): Stored access token for API calls (should be encrypted in production).
        created_at (datetime): Timestamp of user registration.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    github_username = Column(String, index=True)
    github_email = Column(String, nullable=True)
    github_access_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

