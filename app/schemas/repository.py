"""
Repository Schemas

This module defines the Pydantic models for Repository-related operations,
including data validation for connection requests and API responses.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RepositoryBase(BaseModel):
    """Base Pydantic model for shared Repository attributes."""
    name: str
    full_name: str
    repo_url: str
    is_private: bool
    default_branch: str

class RepositoryConnect(BaseModel):
    """Pydantic model for receiving repository connection requests."""
    github_repo_id: int

class RepositoryCreate(RepositoryBase):
    """Pydantic model for creating a new Repository entry in the database."""
    github_repo_id: int
    owner_name: str

class RepositoryResponse(RepositoryBase):
    """Pydantic model for returning Repository data in API responses."""
    id: int
    github_repo_id: int
    owner_name: str
    connected_by_user_id: int
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True

