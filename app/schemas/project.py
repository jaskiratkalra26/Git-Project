"""
Project Schemas

This module defines the Pydantic models (data transfer objects) for Project-related operations.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    """Base Pydantic model for shared Project attributes."""
    project_name: str
    description: str
    features: List[str]

class ProjectCreate(ProjectBase):
    """Pydantic model for creating a new Project."""
    repository_id: int
    created_by: int

class ProjectResponse(ProjectBase):
    """Pydantic model for returning Project data in API responses."""
    id: int
    repository_id: int
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True

