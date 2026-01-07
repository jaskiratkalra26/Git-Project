from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    project_name: str
    description: str
    features: List[str]

class ProjectCreate(ProjectBase):
    repository_id: int
    created_by: int

class ProjectResponse(ProjectBase):
    id: int
    repository_id: int
    created_at: datetime

    class Config:
        from_attributes = True
