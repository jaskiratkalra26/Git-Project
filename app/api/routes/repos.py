from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_repos():
    return {"message": "ok"}
