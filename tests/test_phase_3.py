import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Ensure we can import app modules
import sys
sys.path.append(os.getcwd())

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.models.user import User
from app.services.github_service import verify_access_token

# Load environment variables
load_dotenv()

# Setup In-Memory SQLite Database for Testing
# "check_same_thread": False is crucial for SQLite in-memory with FastAPI TestClient
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_phase_3_full_flow(test_db):
    print("\n--- Starting Phase 3 Integration Test ---")
    
    # 1. Get Access Token
    access_token = os.getenv("access_token")
    if not access_token:
        pytest.fail("Skipping: 'access_token' not found in .env file.")
    
    # Clean quotes if present
    access_token = access_token.strip('"').strip("'")

    # 2. Setup: Get Real User ID from GitHub to simulate login
    print("[SETUP] Verifying Access Token with GitHub...")
    try:
        github_profile = await verify_access_token(access_token)
    except Exception as e:
        pytest.fail(f"Failed to verify token: {e}")

    github_id = github_profile["id"]
    username = github_profile["login"]
    print(f"[SETUP] User verified: {username} (ID: {github_id})")

    # 3. Setup: Insert User into Test Database
    print("[SETUP] Creating User in Test Database...")
    db = TestingSessionLocal()
    user = User(
        github_id=github_id,
        github_username=username,
        github_access_token=access_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 4. Action: List Repositories (GET /repos)
    print("[ACTION] Fetching repositories (GET /repos)...")
    response = client.get("/repos/", headers=headers)
    
    if response.status_code != 200:
        pytest.fail(f"API Error: {response.text}")
        
    repos = response.json()
    assert isinstance(repos, list)
    if len(repos) == 0:
        pytest.fail("GitHub user has 0 repositories. Cannot test 'connect' feature.")
        
    print(f"[ASSERT] Found {len(repos)} repositories.")
    
    # 5. Action: Connect a Repository (POST /repos/connect)
    target_repo = repos[0]
    repo_id_to_connect = target_repo["id"]
    repo_name = target_repo["name"]
    
    print(f"[ACTION] Connecting repository: {repo_name} (ID: {repo_id_to_connect})...")
    
    connect_payload = {"github_repo_id": repo_id_to_connect}
    connect_response = client.post("/repos/connect", json=connect_payload, headers=headers)
    
    if connect_response.status_code != 200:
         pytest.fail(f"Connect Logic Failed: {connect_response.text}")

    connected_data = connect_response.json()
    
    # 6. Validate Connection
    assert connected_data["github_repo_id"] == repo_id_to_connect
    assert connected_data["name"] == repo_name
    assert connected_data["connected_by_user_id"] == user.id
    assert "id" in connected_data
    
    print(f"[ASSERT] Repository connected successfully. Local ID: {connected_data['id']}")
    
    # 7. Action: Connect Same Repository Again (Idempotency)
    print("[ACTION] Connecting same repository again (Checking idempotency)...")
    dup_response = client.post("/repos/connect", json=connect_payload, headers=headers)
    
    assert dup_response.status_code == 200
    dup_data = dup_response.json()
    
    assert dup_data["id"] == connected_data["id"]
    print("[ASSERT] Duplicate connection returned existing record correctly.")

    print("--- Phase 3 Test Passed ---\n")
