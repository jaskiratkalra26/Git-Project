import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.db.base import Base
from app.api.dependencies import get_current_user
from fastapi import Depends, APIRouter
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Get token from .env and clean it
ACCESS_TOKEN = os.getenv("access_token")
if ACCESS_TOKEN and ACCESS_TOKEN.startswith('"') and ACCESS_TOKEN.endswith('"'):
    ACCESS_TOKEN = ACCESS_TOKEN[1:-1]

# Add a protected route for testing dependency
mock_router = APIRouter()

@mock_router.get("/test-protected")
def protected_route(user = Depends(get_current_user)):
    return {"user_id": user.id, "username": user.github_username}

app.include_router(mock_router)

def test_1_verify_token_valid():
    """Test that a valid GitHub token can authenticate and create a user."""
    if not ACCESS_TOKEN:
        pytest.skip("access_token not found in .env")
    
    print(f"\nTesting with token: {ACCESS_TOKEN[:4]}...{ACCESS_TOKEN[-4:]}")
    
    response = client.post(
        "/auth/verify-token",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
        
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "github_username" in data
    print(f"Successfully authenticated as: {data['github_username']}")

def test_2_verify_token_invalid():
    """Test that an invalid token is rejected."""
    response = client.post(
        "/auth/verify-token",
        headers={"Authorization": "Bearer invalid_token_123"}
    )
    assert response.status_code == 401

def test_3_protected_route_access():
    """Test that the authenticated user can access a protected route."""
    if not ACCESS_TOKEN:
        pytest.skip("access_token not found in .env")
        
    # Ensure user exists (in case test_1 failed or order changed)
    client.post(
        "/auth/verify-token",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    # Access protected route
    response = client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "username" in data

def test_4_protected_route_no_auth():
    """Test that accessing a protected route without a token fails."""
    response = client.get("/test-protected")
    # FastAPI HTTPBearer raises 403 when header is missing, but sometimes 401 depending on version/config
    assert response.status_code in [401, 403]
