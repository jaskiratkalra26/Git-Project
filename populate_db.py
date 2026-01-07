import asyncio
import os
from dotenv import load_dotenv
from app.db.database import SessionLocal
from app.models.user import User
from app.models.repository import Repository
from app.services.github_service import verify_access_token, get_user_repositories, get_repository_details

load_dotenv()
raw_token = os.getenv('access_token')
if not raw_token:
    print("Error: access_token not found in .env")
    exit(1)

access_token = raw_token.replace('"', '').replace("'", '').strip()

async def populate():
    db = SessionLocal()
    try:
        print("1. Verifying Token...")
        github_profile = await verify_access_token(access_token)
        github_id = github_profile['id']
        username = github_profile['login']
        print(f"   Authenticated as: {username} ({github_id})")

        # 2. Upsert User
        print("2. Updating/Creating User in DB...")
        user = db.query(User).filter(User.github_id == github_id).first()
        if user:
            print("   User found. Updating token.")
            user.github_access_token = access_token
        else:
            print("   User not found. Creating new.")
            user = User(
                github_id=github_id,
                github_username=username,
                github_access_token=access_token
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        print(f"   User DB ID: {user.id}")

        # 3. Ensure a Repo exists (Multimodal-RAG-Engine)
        repo_id = 1110012547 # Multimodal-RAG-Engine ID
        print(f"3. Checking Repository (GitHub ID: {repo_id})...")
        
        repo = db.query(Repository).filter(Repository.github_repo_id == repo_id).first()
        if not repo:
            print("   Repo not found locally. Connecting...")
            details = await get_repository_details(access_token, repo_id)
            repo = Repository(
                github_repo_id=details['github_repo_id'],
                name=details['name'],
                full_name=details['full_name'],
                repo_url=details['repo_url'],
                is_private=details['is_private'],
                default_branch=details['default_branch'],
                owner_name=details['owner_name'],
                connected_by_user_id=user.id
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)
        
        print(f"   Repo Ready. Local ID: {repo.id}")
        print("SUCCESS: Database populated.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate())
