import httpx
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
