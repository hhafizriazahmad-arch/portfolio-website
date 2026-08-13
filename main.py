import os
import json
import urllib.request
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
            # Clean up removed projects if previously seeded
            db.query(models.Project).filter_by(title="Autonomous AI Voice Agent & Receptionist").delete()
            db.query(models.Project).filter_by(title="Autonomous Lead Intelligence System").delete()
            db.query(models.Project).filter_by(title="Autonomous AI Cold Prospecting & Web-Research Agent").delete()
            db.commit()

            default_projects = [
                {
                    "title": "Digital Marketing Web Suite",
                    "description": "Full-stack digital marketing platform featuring an interactive dynamic UI, serverless backend integrations, and automated lead intelligence data pipelines.",
                    "tech_stack": "Full-Stack Web Dev, JavaScript, Python, REST API, HTML5/CSS3, Vercel",
                    "github_url": "https://github.com/hhafizriazahmad-arch/digital-marketing",
                    "live_url": "https://digital-marketing-sand.vercel.app",
                    "icon_type": "cpu"
                },
                {
                    "title": "E-Commerce Order Processing Engine",
                    "description": "A high-performance order processing engine that handles asynchronous orders, logs requests to an SQLite database, and broadcasts live update notifications. Designed for maximum throughput and reliability.",
                    "tech_stack": "Python, FastAPI, SQLite, Asynchronous Tasks, Uvicorn",
                    "github_url": "https://github.com/hhafizriazahmad-arch/fluxflow-ecommerce-engine",
                    "live_url": "https://fluxflow-ecommerce-engine.vercel.app",
                    "icon_type": "shopping-cart"
                },
                {
                    "title": "Onboarding Automation System",
                    "description": "An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time onboarding notifications via Slack webhook integrations.",
                    "tech_stack": "Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
                    "github_url": "https://github.com/hhafizriazahmad-arch/onboarding-automation-system",
                    "live_url": None,
                    "icon_type": "cpu"
                },
                {
                    "title": "AI Lead Intelligence System",
                    "description": "An automated B2B lead generation pipeline engineered to identify, enrich, and qualify profiles of agency founders and CEOs across the US, UK, and Canada. Built on a serverless architecture for high-impact prospect research.",
                    "tech_stack": "Python, FastAPI, Playwright, Gemini AI, HubSpot API, Slack Webhooks, Vercel",
                    "github_url": "https://github.com/hhafizriazahmad-arch/ai-lead-intelligence-system",
                    "live_url": "https://ai-lead-intelligence-system.vercel.app",
                    "icon_type": "database"
                }
            ]
            for p_data in default_projects:
                existing = db.query(models.Project).filter_by(title=p_data["title"]).first()
                if not existing:
                    db.add(models.Project(**p_data))
                else:
                    existing.github_url = p_data["github_url"]
                    existing.live_url = p_data.get("live_url")
                    existing.description = p_data["description"]
                    existing.tech_stack = p_data["tech_stack"]
                    existing.icon_type = p_data.get("icon_type", "default")
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

def forward_lead_to_webhook(name: str, email: str, subject: str, message: str) -> bool:
    """Forward contact/lead details to Google Apps Script Webhook."""
    webhook_url = os.getenv(
        "GOOGLE_APPS_SCRIPT_WEBHOOK_URL",
        "https://script.google.com/macros/s/AKfycbwRw_vv_nKvnHr8JDp_cYR7xV-JHU6Qr5qOmUCmuy_J34SR0RZLpJ0D1cvwhFn_tFNiLw/exec"
    )
    payload = json.dumps({
        "name": name,
        "email": email,
        "subject": subject,
        "message": message
    }).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "text/plain;charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Webhook forwarded successfully, status code: {response.getcode()}")
            return True
    except Exception as webhook_err:
        print(f"Warning: Failed to forward payload to Google Apps Script webhook: {webhook_err}")
        return False

@app.post("/api/contact", response_model=schemas.ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def submit_contact_form(message: schemas.ContactRequest, db: Session = Depends(get_db)):
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
        forward_lead_to_webhook(message.name, message.email, message.subject, message.message)

        return db_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving your message: {str(e)}"
        )

import re

SYSTEM_PROMPT = (
    "You are a friendly, conversational AI assistant representing Hafiz Riaz Ahmad, "
    "an expert automation engineer who builds B2B lead generation pipelines and backend systems. "
    "Speak naturally like a human, keep responses concise, and never repeat yourself. "
    "If a user expresses interest in working together, politely and naturally ask for their name and email."
)

def extract_lead_info_from_messages(messages: list) -> tuple[str | None, str | None]:
    """Autonomous extraction of email and name from conversational chat history."""
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    found_email = None
    found_name = None

    for m in reversed(messages):
        if m.role == 'user':
            text = m.content
            email_match = email_regex.search(text)
            if email_match:
                found_email = email_match.group(0).strip()
                name_match = re.search(r'(?:my name is|i am|i\'m)\s+([A-Za-z\s]{2,30})', text, re.IGNORECASE)
                if name_match:
                    found_name = name_match.group(1).strip()
                else:
                    clean_text = email_regex.sub('', text).strip()
                    clean_text = re.sub(r'[^a-zA-Z\s]', '', clean_text).strip()
                    words = [w for w in clean_text.split() if w.lower() not in ['my', 'name', 'is', 'email', 'and', 'to', 'for', 'submitting', 'info']]
                    if words and len(words) <= 4:
                        found_name = " ".join(words).title()
                    else:
                        email_prefix = found_email.split('@')[0]
                        found_name = re.sub(r'[^a-zA-Z]', ' ', email_prefix).title().strip() or "Chat Lead"
                break

    return found_name, found_email

@app.post("/api/chat", response_model=schemas.ChatResponse)
def handle_chat_message(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """Handle chat messages by routing directly to Gemini API with full conversational memory and strict error handling."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    lead_captured = False

    # Autonomous lead extraction from chat history / payload
    name_extracted, email_extracted = extract_lead_info_from_messages(request.messages)
    if request.name:
        name_extracted = request.name.strip()
    if request.email:
        email_extracted = request.email.strip()

    if email_extracted and name_extracted:
        try:
            existing_lead = db.query(models.ContactMessage).filter(
                models.ContactMessage.email == email_extracted,
                models.ContactMessage.subject == "AI Chatbot Conversational Lead"
            ).first()

            if not existing_lead:
                conversation_transcript = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in request.messages])
                db_msg = models.ContactMessage(
                    name=name_extracted,
                    email=email_extracted,
                    subject="AI Chatbot Conversational Lead",
                    message=f"Chat Transcript:\n{conversation_transcript}"
                )
                db.add(db_msg)
                db.commit()

                # Automatically & invisibly forward lead payload to Google Sheets Webhook
                forward_lead_to_webhook(
                    name=name_extracted,
                    email=email_extracted,
                    subject="AI Chatbot Conversational Lead",
                    message=conversation_transcript
                )
                lead_captured = True
        except Exception as e:
            print(f"Error executing autonomous chat lead capture: {e}")

    # Gemini API integration with conversation memory
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return schemas.ChatResponse(
            reply="I am currently offline, please try again later or use the contact form below.",
            lead_captured=lead_captured,
            prompt_lead_capture=False
        )

    ai_reply = None
    try:
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        contents = [
            {"role": "user", "parts": [{"text": f"System Context: {SYSTEM_PROMPT}"}]}
        ]
        for m in request.messages[-10:]:
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        payload = json.dumps({"contents": contents}).encode("utf-8")
        req = urllib.request.Request(
            gemini_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    ai_reply = parts[0].get("text", "").strip()
    except Exception as gemini_err:
        print(f"Gemini API execution error: {gemini_err}")
        return schemas.ChatResponse(
            reply="I am currently offline, please try again later or use the contact form below.",
            lead_captured=lead_captured,
            prompt_lead_capture=False
        )

    if not ai_reply:
        ai_reply = "I am currently offline, please try again later or use the contact form below."

    return schemas.ChatResponse(
        reply=ai_reply,
        lead_captured=lead_captured,
        prompt_lead_capture=False
    )

# Serve static frontend files relative to application root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


