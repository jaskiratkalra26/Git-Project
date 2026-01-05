from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True)
    github_username = Column(String, index=True)
    github_email = Column(String, nullable=True)
    github_access_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
