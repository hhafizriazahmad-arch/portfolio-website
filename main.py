import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Initialize database tables gracefully
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

# Explicitly export FastAPI application instance
app = FastAPI(
    title="Hafiz Riaz Portfolio API",
    description="Backend API for portfolio website and contact submissions",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed database with projects if empty
def seed_projects():
    try:
        db = next(get_db())
        try:
            project_count = db.query(models.Project).count()
            if project_count == 0:
                projects = [
                    models.Project(
                        title="E-Commerce Order Processing Engine",
                        description="A high-performance order processing engine that handles asynchronous orders, logs requests to an SQLite database, and broadcasts live update notifications. Designed for maximum throughput and reliability.",
                        tech_stack="Python, FastAPI, SQLite, Asynchronous Tasks, Uvicorn",
                        github_url="https://github.com/hafizriaz/ecommerce-order-engine",
                        live_url=None,
                        icon_type="shopping-cart"
                    ),
                    models.Project(
                        title="Onboarding Automation System",
                        description="An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time onboarding notifications via Slack webhook integrations.",
                        tech_stack="Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
                        github_url="https://github.com/hafizriaz/onboarding-automation",
                        live_url=None,
                        icon_type="cpu"
                    )
                ]
                db.add_all(projects)
                db.commit()
                print("Successfully seeded portfolio projects.")
        except Exception as e:
            db.rollback()
            print(f"Error seeding projects: {e}")
        finally:
            db.close()
    except Exception as e:
        print(f"Error accessing DB during seed: {e}")

seed_projects()

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Fetch all projects from the database."""
    try:
        projects = db.query(models.Project).all()
        return projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []

@app.post("/api/contact", response_model=schemas.ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(message: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    """Save contact form message to the database."""
    try:
        db_message = models.ContactMessage(
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving your message: {str(e)}"
        )

# Serve static frontend files relative to application root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
