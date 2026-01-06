import asyncio
import os
from dotenv import load_dotenv
from app.services.github_service import verify_access_token, get_user_repositories

load_dotenv()
# Clean the token string
raw_token = os.getenv('access_token')
if raw_token:
    access_token = raw_token.replace('"', '').replace("'", '').strip()
else:
    print("Error: access_token not found in .env")
    exit(1)

async def list_repos():
    try:
        print(f"Fetching list of repositories for user...")
        repos = await get_user_repositories(access_token)
        if not repos:
            print("No repositories found.")
            return
            
        print(f"\nFound {len(repos)} repositories:")
        print("-" * 50)
        for i, repo in enumerate(repos):
            print(f"{i+1}. {repo['name']} (ID: {repo['id']}) - {repo['html_url']}")
        print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_repos())
