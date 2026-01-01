from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_projects():
    return {"message": "ok"}
