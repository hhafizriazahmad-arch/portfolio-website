from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

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

seed_projects()

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Fetch all projects from the database."""
    projects = db.query(models.Project).all()
    return projects

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

# Serve static frontend files
# This must be mounted last to ensure it does not override /api routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")
