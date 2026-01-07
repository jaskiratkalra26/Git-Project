import httpx
import base64
from fastapi import HTTPException, status

GITHUB_API_URL = "https://api.github.com"

async def verify_access_token(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/user", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid GitHub access token"
            )
            
        return response.json()

async def get_user_repositories(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Fetching repositories with basic pagination support (page 1, 100 per page to get most)
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
        
        # Extract relevant fields
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

async def get_repository_details(access_token: str, github_repo_id: int):
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
        
        # Extract fields matching our model requirements
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
            
        # Decode Base64 to UTF-8 string
        try:
            return base64.b64decode(content_b64).decode("utf-8")
        except Exception:
            # Fallback or error if decoding fails (though it shouldn't for valid Base64)
            return ""


