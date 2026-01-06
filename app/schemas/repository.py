from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RepositoryBase(BaseModel):
    name: str
    full_name: str
    repo_url: str
    is_private: bool
    default_branch: str

class RepositoryConnect(BaseModel):
    github_repo_id: int

class RepositoryCreate(RepositoryBase):
    github_repo_id: int
    owner_name: str

class RepositoryResponse(RepositoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
