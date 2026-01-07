import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def verify_token():
    raw_token = os.getenv("access_token")
    if not raw_token:
        print("FAIL: No token found in .env")
        return

    token = raw_token.strip().strip('"').strip("'")
    print(f"Testing Token: {token[:4]}...{token[-4:]}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code == 200:
            print(f"SUCCESS: Token valid. Logged in as: {response.json().get('login')}")
        else:
            print(f"FAIL: GitHub returned {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(verify_token())
