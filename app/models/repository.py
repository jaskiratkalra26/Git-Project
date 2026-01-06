from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class Repository(Base):
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
