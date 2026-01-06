import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.repository import Repository
from app.services.github_service import verify_access_token, get_repository_details, get_user_repositories

load_dotenv()
# Clean the token string very carefully
raw_token = os.getenv('access_token')
if raw_token:
    access_token = raw_token.replace('"', '').replace("'", '').strip()
else:
    print("Error: access_token not found in .env")
    exit(1)

async def populate_db():
    db = SessionLocal()
    try:
        print(f"Using Token: {access_token[:4]}...{access_token[-4:]}")
        
        # 1. Verify User
        print('Verifying token...')
        try:
            github_user = await verify_access_token(access_token)
        except Exception as e:
            print(f"Token verification failed: {e}")
            return

        github_id = github_user['id']
        username = github_user['login']
        
        # 2. Get/Create User in DB
        user = db.query(User).filter(User.github_id == github_id).first()
        if not user:
            print(f'Creating user {username}...')
            user = User(github_id=github_id, github_username=username, github_access_token=access_token)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f'User {username} found (ID: {user.id})')

        # 3. List Repos to pick one
        print('Fetching repos from GitHub...')
        repos = await get_user_repositories(access_token)
        if not repos:
            print('No repos found on GitHub.')
            return

        # Pick the first one for demonstration
        target = repos[0] 
        print(f'Selected Repo: {target["name"]} (GitHub ID: {target["id"]})')
        
        # 4. Connect Repo
        existing = db.query(Repository).filter(Repository.github_repo_id == target['id']).first()
        if existing:
             print('Repo already connected in DB.')
        else:
             print('Connecting to local DB...')
             details = await get_repository_details(access_token, target['id'])
             
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
             print('SUCCESS: Repository populated!')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate_db())
