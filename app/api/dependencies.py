"""
API Dependencies

This module defines FastAPI dependencies, particularly for authentication and
database session injection.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.github_service import verify_access_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that authenticates the user via GitHub token.

    Args:
        credentials (HTTPAuthorizationCredentials): The bearer token.
        db (Session): The database session.

    Returns:
        User: The authenticated user model instance.

    Raises:
        HTTPException: If the token is invalid or the user does not exist in the local DB.
    """
    token = credentials.credentials
    
    try:
        # Verify token with GitHub to ensure it is still valid
        github_user = await verify_access_token(token)
        github_id = github_user.get("id")
        
        if not github_id:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid GitHub token",
            )

        # Fetch user from DB
        user = db.query(User).filter(User.github_id == github_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
            
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

# Re-export get_db for use in other modules
__all__ = ["get_db", "get_current_user"]

