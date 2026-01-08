"""
Main Application Entry Point

This module initializes the FastAPI application, configures the database,
and registers all the API routers.
"""

from fastapi import FastAPI
from app.api.routes import auth, repos, projects
from app.db.database import engine
from app.models import user, repository, project  # Import models to register them with Base
from app.db.base import Base

# Create database tables automatically on startup
# In production, use Alembic for value migrations instead of this.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GitHub Project Generator API",
    description="API for parsing GitHub READMEs and generating project summaries using Ollama",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Welcome to the API"}

@app.get("/ping")
def ping():
    """Simple ping endpoint for monitoring."""
    return {"status": "ok"}

# Register Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(repos.router, prefix="/repos", tags=["repos"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])

