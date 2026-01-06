import asyncio
import os
from dotenv import load_dotenv
from app.db.database import SessionLocal
from app.models.user import User
from app.models.repository import Repository
from app.services.github_service import verify_access_token, get_repository_details

load_dotenv()
# Clean the token string
raw_token = os.getenv('access_token')
if raw_token:
    access_token = raw_token.replace('"', '').replace("'", '').strip()
else:
    print("Error: access_token not found in .env")
    exit(1)

# Target Repo ID for "Multimodal-RAG-Engine" from your list
TARGET_REPO_ID = 1110012547

async def connect_specifc_repo():
    db = SessionLocal()
    try:
        # 1. Get User (Assume exists from previous run, but verify)
        print('Verifying user...')
        github_user = await verify_access_token(access_token)
        user = db.query(User).filter(User.github_id == github_user['id']).first()
        
        if not user:
            print("User not found in DB. Please run populate_db.py first to create user.")
            return

        # 2. Check overlap
        existing = db.query(Repository).filter(Repository.github_repo_id == TARGET_REPO_ID).first()
        if existing:
            print(f'Repository already connected! (Local ID: {existing.id})')
            return

        # 3. Fetch & Connect
        print(f'Connecting Repo ID: {TARGET_REPO_ID} (Multimodal-RAG-Engine)...')
        details = await get_repository_details(access_token, TARGET_REPO_ID)
        
        new_repo = Repository(
            github_repo_id=details['github_repo_id'],
            name=details['name'],
            full_name=details['full_name'],
            repo_url=details['repo_url'],
            is_private=details['is_private'],
            default_branch=details['default_branch'],
            owner_name=details['owner_name'],
            connected_by_user_id=user.id
        )
        
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        
        print(f'SUCCESS: Connected "{new_repo.name}"')
        print(f'  - Local DB ID: {new_repo.id}')
        print(f'  - GitHub URL: {new_repo.repo_url}')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(connect_specifc_repo())
