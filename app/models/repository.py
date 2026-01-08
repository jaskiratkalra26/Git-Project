"""
Repository Model

This module defines the database schema for Repositories, which map to 
source code repositories (e.g., from GitHub).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class Repository(Base):
    """
    SQLAlchemy model representing a GitHub Repository.

    Attributes:
        id (int): Primary key (internal database ID).
        github_repo_id (int): Description unique ID from GitHub.
        name (str): Repository name.
        full_name (str): Full repository name (owner/name).
        repo_url (str): HTML URL to the repository.
        is_private (bool): Flag indicating if the repository is private.
        default_branch (str): The default branch name (e.g., main, master).
        owner_name (str): The username of the repository owner.
        connected_by_user_id (int): Foreign key to the User who connected this repo.
        created_at (datetime): Timestamp of connection.
    """
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    full_name = Column(String)
    repo_url = Column(String)
    is_private = Column(Boolean)
    default_branch = Column(String)
    owner_name = Column(String)
    connected_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

