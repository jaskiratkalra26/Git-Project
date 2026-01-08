"""
Repository Routes

This module handles repository-related endpoints, including listing user repositories
from GitHub and connecting them to the local application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.services.github_service import get_user_repositories, get_repository_details
from app.models.user import User
from app.models.repository import Repository
from app.schemas.repository import RepositoryConnect, RepositoryResponse

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_user_repositories(
    current_user: User = Depends(get_current_user),
):
    """
    Fetch repositories for the authenticated user from GitHub.

    Args:
        current_user (User): The authenticated user.

    Returns:
        List[Dict[str, Any]]: A list of repositories from GitHub.
    """
    if not current_user.github_access_token:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no GitHub access token",
            )
            
    try:
        repos = await get_user_repositories(current_user.github_access_token)
        return repos
    except Exception as e:
        # In a real app, we might want to log this error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error fetching repositories: {str(e)}"
        )

@router.post("/connect", response_model=RepositoryResponse)
async def connect_repository(
    repo_in: RepositoryConnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect a GitHub repository to the user's account by ID.
    Fetches the latest metadata from GitHub and stores it in the database.

    Args:
        repo_in (RepositoryConnect): The payload containing the GitHub repository ID.
        current_user (User): The authenticated user.
        db (Session): Database session.

    Returns:
        RepositoryResponse: The connected repository details.
    """
    if not current_user.github_access_token:
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no GitHub access token",
            )

    # Check if repository already exists in DB
    existing_repo = db.query(Repository).filter(Repository.github_repo_id == repo_in.github_repo_id).first()
    if existing_repo:
        return existing_repo

    try:
        # Fetch fresh details from GitHub
        repo_details = await get_repository_details(current_user.github_access_token, repo_in.github_repo_id)
        
        # Create new repository record
        new_repo = Repository(
            github_repo_id=repo_details["github_repo_id"],
            name=repo_details["name"],
            full_name=repo_details["full_name"],
            repo_url=repo_details["repo_url"],
            is_private=repo_details["is_private"],
            default_branch=repo_details["default_branch"],
            owner_name=repo_details["owner_name"],
            connected_by_user_id=current_user.id
        )

        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        
        return new_repo

    except HTTPException as e:
        raise e
    except Exception as e:
        # In a real app, we might want to log this error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error connecting repository: {str(e)}"
        )
