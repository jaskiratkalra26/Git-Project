import pytest
import os
import sqlite3
import httpx
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Ensure we can import app modules
import sys
sys.path.append(os.getcwd())

from app.main import app
from app.db.database import get_db

# Load environment variables
load_dotenv()

client = TestClient(app)

# We will use the REAL database (app.db) because:
# 1. We need the Repositories we created in Phase 3
# 2. We want to test the full E2E flow including Ollama

def test_phase_5_generation():
    print("\n--- Starting Phase 5 Integration Test ---")
    
    # 1. Get Access Token
    access_token = os.getenv("access_token") 
    if not access_token:
        pytest.fail("Skipping: 'access_token' not found in .env file.")
    
    # Clean quotes if present
    access_token = access_token.strip('"').strip("'")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Verify we have a connected repo in the DB
    # Repo ID 2 corresponds to Multimodal-RAG-Engine (created by populate_db.py)
    TARGET_REPO_ID = 2
    
    print(f"[ACTION] Triggering Generation for Repository ID: {TARGET_REPO_ID}...")
    
    # Timeout increased because LLMs can be slow
    response = client.post(f"/projects/generate/{TARGET_REPO_ID}", headers=headers, timeout=120)
    
    if response.status_code != 200:
        pytest.fail(f"API Error ({response.status_code}): {response.text}")
        
    project_data = response.json()
    
    # 3. Validation Logic
    print("\n[VALIDATION] Analyzing LLaMA Output:")
    print(json.dumps(project_data, indent=2))
    
    # Check Structure
    assert "id" in project_data
    assert "project_name" in project_data
    assert "description" in project_data
    assert "features" in project_data
    
    # Check Content Quality (Heuristic)
    assert len(project_data["project_name"]) > 0, "Project Name is empty"
    assert len(project_data["description"]) > 10, "Description is too short to be useful"
    assert isinstance(project_data["features"], list), "Features must be a list"
    assert len(project_data["features"]) > 0, "No features were extracted"
    
    print("\n[SUCCESS] Project information extracted and stored successfully!")
    print(f" - Verified Project: {project_data['project_name']}")
    print(f" - Extracted Features: {len(project_data['features'])}")

if __name__ == "__main__":
    test_phase_5_generation()
