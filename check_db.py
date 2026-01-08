"""
Database Verification Script

This script helps verify the content of the local database by printing the most
recently created project. Useful for debugging without a GUI.
"""

from app.db.database import SessionLocal
from app.models.project import Project
import json

def check_latest_project():
    """
    Queries and prints details of the most recently created project.
    """
    db = SessionLocal()
    try:
        # Get the most recent project
        project = db.query(Project).order_by(Project.id.desc()).first()
        
        if project:
            print(f"--- Latest Project (ID: {project.id}) ---")
            print(f"Name: {project.project_name}")
            print(f"Description: {project.description}")
            print(f"Features: {project.features}")
            print(f"Repo ID: {project.repository_id}")
            print(f"Created At: {project.created_at}")
        else:
            print("No projects found in the database.")
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print(">>>>>>>> START DB CHECK <<<<<<<<")
    check_latest_project()
    print(">>>>>>>> END DB CHECK <<<<<<<<")
