from fastapi import FastAPI
from app.api.routes import auth, repos, projects
from app.db.database import engine
from app.models import user  # Import models to register them with Base
from app.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(repos.router, prefix="/repos", tags=["repos"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
