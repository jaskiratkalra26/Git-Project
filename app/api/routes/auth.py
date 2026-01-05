from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.github_service import verify_access_token
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()
security = HTTPBearer()

@router.post("/verify-token", response_model=UserResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    
    # Verify token with GitHub
    github_user = await verify_access_token(token)
    
    # Extract user info
    github_id = github_user.get("id")
    username = github_user.get("login")
    email = github_user.get("email")
    
    if not github_id or not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete GitHub user data"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.github_id == github_id).first()
    
    if user:
        # Update existing user
        user.github_access_token = token
        user.github_username = username
        user.github_email = email
    else:
        # Create new user
        user = User(
            github_id=github_id,
            github_username=username,
            github_email=email,
            github_access_token=token
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(user_id=user.id, github_username=user.github_username)
