"""
GitHub Service Module

This module handles interactions with the GitHub API. It includes functionality for
verifying access tokens, fetching user repositories, retrieving repository details,
and downloading README content.
"""

import httpx
import base64
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, status
from app.core.config import GITHUB_API_URL

async def verify_access_token(access_token: str) -> Dict[str, Any]:
    """
    Verifies the validity of a GitHub access token by making a request to the user endpoint.

    Args:
        access_token (str): The GitHub personal access token or OAuth token.

    Returns:
        Dict[str, Any]: The user profile data if the token is valid.

    Raises:
        HTTPException: If the token is invalid or the request fails (401 Unauthorized).
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Check against the GitHub user endpoint to specific validity
        response = await client.get(f"{GITHUB_API_URL}/user", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid GitHub access token"
            )
            
        return response.json()

async def get_user_repositories(access_token: str) -> List[Dict[str, Any]]:
    """
    Fetches the authenticated user's repositories from GitHub.

    Args:
        access_token (str): The GitHub access token.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing simplified repository information.
            Each dictionary contains: id, name, full_name, html_url, private, default_branch, owner_login.

    Raises:
        HTTPException: If the request to GitHub fails.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Fetching repositories with basic pagination support (page 1, 100 per page to get most)
        # TODO: Implement full pagination to support users with > 100 repositories
        response = await client.get(
            f"{GITHUB_API_URL}/user/repos", 
            headers=headers,
            params={"per_page": 100, "sort": "updated"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch repositories from GitHub"
            )
            
        repos_data = response.json()
        
        # Extract relevant fields to minimize data transfer and processing
        cleaned_repos = []
        for repo in repos_data:
            cleaned_repos.append({
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "html_url": repo.get("html_url"),
                "private": repo.get("private"),
                "default_branch": repo.get("default_branch"),
                "owner_login": repo.get("owner", {}).get("login")
            })
            
        return cleaned_repos

async def get_repository_details(access_token: str, github_repo_id: int) -> Dict[str, Any]:
    """
    Retrieves detailed information for a specific repository.

    Args:
        access_token (str): The GitHub access token.
        github_repo_id (int): The unique identifier of the GitHub repository.

    Returns:
        Dict[str, Any]: detailed information about the repository including:
            github_repo_id, name, full_name, repo_url, is_private, default_branch, owner_name.

    Raises:
        HTTPException: If the repository is not found (404) or other API errors occur.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_URL}/repositories/{github_repo_id}", 
            headers=headers
        )
        
        if response.status_code != 200:
            status_code = response.status_code
            if status_code == 404:
                detail = "Repository not found or access denied"
            else:
                detail = "Failed to fetch repository details from GitHub"
                
            raise HTTPException(
                status_code=status_code,
                detail=detail
            )
            
        repo_data = response.json()
        
        # Extract fields matching our internal model requirements
        return {
            "github_repo_id": repo_data.get("id"),
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "repo_url": repo_data.get("html_url"),
            "is_private": repo_data.get("private"),
            "default_branch": repo_data.get("default_branch"),
            "owner_name": repo_data.get("owner", {}).get("login")
        }

async def get_readme_content(access_token: str, full_name: str) -> str:
    """
    Fetches and decodes the README file content for a given repository.

    Args:
        access_token (str): The GitHub access token.
        full_name (str): The full name of the repository (e.g., "owner/repo").

    Returns:
        str: The content of the README file as a string. Returns an empty string if not found.

    Raises:
        HTTPException: If the GitHub API returns an error other than 404.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # GET /repos/{owner}/{repo}/readme
        response = await client.get(
            f"{GITHUB_API_URL}/repos/{full_name}/readme", 
            headers=headers
        )
        
        if response.status_code == 404:
            return ""  # README not found, return empty string
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch README from GitHub"
            )
            
        data = response.json()
        content_b64 = data.get("content", "")
        
        if not content_b64:
            return ""
            
        # Decode Base64 content to UTF-8 string
        try:
            return base64.b64decode(content_b64).decode("utf-8")
        except Exception:
            # Fallback for decoding errors (should be rare for valid GitHub responses)
            return ""


