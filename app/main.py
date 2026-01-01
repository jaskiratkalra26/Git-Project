from fastapi import FastAPI
from app.api.routes import auth, repos, projects

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
