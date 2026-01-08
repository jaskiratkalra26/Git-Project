"""
User Schemas

This module defines the Pydantic models for User-related operations.
"""

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    """Base Pydantic model for shared User attributes."""
    github_username: str

class UserCreate(UserBase):
    """Pydantic model for creating a new User."""
    github_id: int
    github_email: str | None = None
    github_access_token: str

class User(UserBase):
    """Pydantic model representing a User (Internal use)."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    """Pydantic model for returning simplified User data."""
    user_id: int
    github_username: str

