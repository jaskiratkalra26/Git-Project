"""
Project Model

This module defines the database schema for Projects, which represent
software projects analyzed or managed within the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime
from app.db.base import Base

class Project(Base):
    """
    SQLAlchemy model representing a Project.
    
    Attributes:
        id (int): Primary key.
        project_name (str): Name of the project.
        description (str): Detailed description of the project.
        features (list): JSON-encoded list of project features.
        repository_id (int): Foreign key to the associated Repository.
        created_by (int): Foreign key to the User who created the project.
        created_at (datetime): Timestamp of creation.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    description = Column(Text)
    features = Column(JSON)  # Storing list of features as JSON
    
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

