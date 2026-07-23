import os
import json
import urllib.request
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

# Seed database with projects if empty or missing default entries
def seed_projects():
    try:
        db = next(get_db())
        try:
            default_projects = [
                {
                    "title": "E-Commerce Order Processing Engine",
                    "description": "A high-performance order processing engine that handles asynchronous orders, logs requests to an SQLite database, and broadcasts live update notifications. Designed for maximum throughput and reliability.",
                    "tech_stack": "Python, FastAPI, SQLite, Asynchronous Tasks, Uvicorn",
                    "github_url": "https://github.com/hafizriaz/ecommerce-order-engine",
                    "live_url": None,
                    "icon_type": "shopping-cart"
                },
                {
                    "title": "Onboarding Automation System",
                    "description": "An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time onboarding notifications via Slack webhook integrations.",
                    "tech_stack": "Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
                    "github_url": "https://github.com/hafizriaz/onboarding-automation",
                    "live_url": None,
                    "icon_type": "cpu"
                },
                {
                    "title": "Autonomous Lead Intelligence System",
                    "description": "An AI-driven autonomous lead generation and intelligence pipeline that automatically discovers, scrapes, and qualifies potential client leads. It aggregates business metrics, performs context analysis, and structures leads directly into a database for automated outreach.",
                    "tech_stack": "Python, AI / LLM Integration, Web Scraping, Data Pipeline, PostgreSQL",
                    "github_url": "https://github.com/hafizriaz/autonomous-lead-intelligence",
                    "live_url": None,
                    "icon_type": "database"
                }
            ]
            for p_data in default_projects:
                existing = db.query(models.Project).filter_by(title=p_data["title"]).first()
                if not existing:
                    db.add(models.Project(**p_data))
            db.commit()
            print("Successfully verified and seeded portfolio projects.")
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
    """Save contact form message to the database and forward to Google Apps Script Webhook."""
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

        # Forward payload to Google Apps Script Webhook
        webhook_url = os.getenv(
            "GOOGLE_APPS_SCRIPT_WEBHOOK_URL",
            "https://script.google.com/macros/s/AKfycbwRw_vv_nKvnHr8JDp_cYR7xV-JHU6Qr5qOmUCmuy_J34SR0RZLpJ0D1cvwhFn_tFNiLw/exec"
        )
        payload = json.dumps({
            "name": message.name,
            "email": message.email,
            "subject": message.subject,
            "message": message.message
        }).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"Webhook forwarded successfully, status code: {response.getcode()}")
        except Exception as webhook_err:
            print(f"Warning: Failed to forward payload to Google Apps Script webhook: {webhook_err}")

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
