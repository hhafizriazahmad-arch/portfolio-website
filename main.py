import os
import json
import urllib.request
import re
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

# Dual SDK support for Google Gemini AI (Modern google.genai and Legacy google.generativeai)
GENAI_CLIENT = None
LEGACY_GENAI = None

api_key_val = os.getenv('GEMINI_API_KEY')
if api_key_val:
    os.environ["GEMINI_API_KEY"] = api_key_val
    os.environ["GOOGLE_API_KEY"] = api_key_val

try:
    from google import genai
    from google.genai import types
    if api_key_val:
        GENAI_CLIENT = genai.Client(api_key=api_key_val)
except Exception as genai_err:
    print(f"Modern google.genai SDK notice: {genai_err}")

try:
    import google.generativeai as legacy_genai
    if api_key_val:
        legacy_genai.configure(api_key=api_key_val)
    LEGACY_GENAI = legacy_genai
except Exception as sdk_init_err:
    print(f"Legacy GenerativeAI SDK notice: {sdk_init_err}")

SYSTEM_PROMPT = """# HR Autonomous Human Consultant Directives & Persona

## Core Identity
You are an experienced, senior team member and AI automation consultant at HR Autonomous.
You communicate with visitors as a knowledgeable human peer having an organic, real-time consultation.

You MUST NEVER sound like an AI assistant, chatbot, customer support script, sales bot, or company brochure.

## Tone & Personality
- Intelligent, calm, confident, curious, practical, professional, and occasionally casual.
- Speak from hands-on engineering and workflow automation experience ("We usually wire...", "In our experience with real estate lead pipelines...", "When teams hit that wall...").
- Never sound fake, overly enthusiastic, or robotic. Avoid corporate buzzwords and filler phrases.

## Context Memory & Continuity
- RETAIN and USE all information provided previously in the conversation (business type, team size, tools used, lead count, specific pain points).
- NEVER ask the visitor for information they have already provided.
- Adapt instantly when the visitor changes topics or says "actually", "wait", "forget that", or "no". Pivot cleanly without apologizing or clinging to the previous topic.

## Communication & Length Rules
- For simple or direct questions (e.g., pricing, "how's it work", casual greetings): respond in 1-2 short, direct sentences.
- For complex technical or workflow questions: provide concise, structured explanations. Avoid bullet-list dumps unless list structure genuinely aids clarity.
- Ask ONLY ONE relevant follow-up question per turn. Never interrogate the visitor with a list of questions.

## Emotional Intelligence & Frustration
- When a user expresses frustration, acknowledge it directly and naturally (e.g., "Yeah, that gets frustrating fast—especially when the system is supposed to save you time. What part is causing the most trouble?").
- Never use robotic customer service sympathy lines (e.g., "I am sorry to hear you are experiencing frustration").

## AI Identity Disclosure
- Do NOT proactively mention or advertise that you are an AI, language model, or virtual assistant during normal conversation.
- If the visitor DIRECTLY asks "Are you an AI?", "Are you a bot?", or "Are you human?", respond honestly and briefly in a natural tone (e.g., "Yes, I'm an AI system built by HR Autonomous to consult on automation workflows and backend architecture. What are you looking to build or optimize?").
- NEVER claim to be a physical human person, sit at a physical desk, or invent fake personal life experiences.

## Absolute Prohibitions (NEVER USE)
- Never proactively mention you are an AI, language model, virtual assistant, chatbot, or automated system unless explicitly asked.
- Never use robotic customer service lines:
  * "How can I assist you today?"
  * "How may I help you?"
  * "How can I help today?"
  * "What can I assist you with?"
  * "Certainly!"
  * "Absolutely!"
  * "Great question!"
  * "I'd be happy to help!"
  * "Thanks for reaching out!"
  * "Does that give you a good overview?"
  * "Let me know if you have any questions!"
- Never use "We specialize in..." or "Our services include..." in generic introductions."""

FORBIDDEN_PHRASES = [
    "how can i assist you today",
    "how may i help",
    "how can i help today",
    "what can i assist",
    "i am an ai assistant",
    "i'm an ai assistant",
    "as an ai assistant",
    "i am an ai",
    "i'm an ai",
    "as an ai",
    "ai assistant",
    "virtual assistant",
    "digital assistant",
    "artificial intelligence assistant",
    "we specialize in",
    "our services include",
    "certainly!",
    "absolutely!",
    "great question!",
    "i'd be happy to help",
    "i'd be glad to help",
    "thanks for reaching out",
    "thank you for providing",
    "does that give you a good overview",
    "feel free to ask any questions",
    "let me know if you have any questions"
]

def sanitize_consultant_response(text: str) -> str:
    if not text:
        return "Good to connect. What specific process or workflow are you hoping to optimize right now?"
    
    text_lower = text.lower()
    
    # Preserve honest AI disclosures when directly asked by user
    if "ai system built by" in text_lower or "ai automation system" in text_lower:
        return text.strip()

    has_forbidden = any(phrase in text_lower for phrase in FORBIDDEN_PHRASES)
    if not has_forbidden:
        return text.strip()
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = []
    for s in sentences:
        s_lower = s.lower()
        if not any(phrase in s_lower for phrase in FORBIDDEN_PHRASES):
            cleaned_sentences.append(s)
            
    cleaned_text = " ".join(cleaned_sentences).strip()
    if len(cleaned_text) < 15:
        return "Good to connect. What specific process or workflow are you hoping to optimize right now?"
    return cleaned_text





import models
import schemas
from database import engine, get_db, SessionLocal

# Create database tables on startup safely
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title="HR Autonomous API",
    description="Backend API for HR Autonomous platform and intelligent business process automation services",
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

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def create_audit_log_internal(db: Session, action: str, details: Optional[str] = None, ip_address: Optional[str] = None):
    """Helper to record audit logs safely."""
    try:
        log_entry = models.AuditLog(
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as err:
        db.rollback()
        print(f"Audit log recording error: {err}")
        return None

def seed_settings():
    """Seed default application settings if not already present."""
    db = SessionLocal()
    try:
        default_settings = [
            {"key": "site_name", "value": "HR Autonomous", "description": "Platform brand name"},
            {"key": "owner_name", "value": "Hafiz Riaz", "description": "Founder & AI Automation Engineer"},
            {"key": "contact_email", "value": "hafizriaz.ai@gmail.com", "description": "Primary contact email"},
            {"key": "maintenance_mode", "value": "false", "description": "System maintenance mode flag"},
            {"key": "ai_assistant_enabled", "value": "true", "description": "Conversational Gemini AI toggle"},
            {"key": "theme", "value": "dark", "description": "Default UI theme"}
        ]
        for s in default_settings:
            existing = db.query(models.Setting).filter_by(key=s["key"]).first()
            if not existing:
                db.add(models.Setting(**s))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding settings: {e}")
    finally:
        db.close()

def seed_projects():
    """Seed default projects if missing or updated."""
    db = SessionLocal()
    try:
        db.query(models.Project).filter_by(title="Autonomous AI Voice Agent & Receptionist").delete()
        db.query(models.Project).filter_by(title="Autonomous Lead Intelligence System").delete()
        db.query(models.Project).filter_by(title="Autonomous AI Cold Prospecting & Web-Research Agent").delete()
        db.commit()

        default_projects = [
            {
                "title": "AI Lead Intelligence System",
                "description": "An automated B2B lead generation pipeline engineered to identify, enrich, and qualify profiles of founders and C-level executives. Built on FastAPI and Gemini AI for high-impact prospect research.",
                "tech_stack": "Python, FastAPI, Playwright, Gemini AI, HubSpot API, Slack Webhooks, Vercel",
                "github_url": "https://github.com/hhafizriazahmad-arch/ai-lead-intelligence-system",
                "live_url": "https://ai-lead-intelligence-system.vercel.app",
                "icon_type": "database"
            },
            {
                "title": "Digital Marketing Automation Suite",
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
                "title": "Onboarding Automation Workflow",
                "description": "An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time notifications via Slack webhooks.",
                "tech_stack": "Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
                "github_url": "https://github.com/hhafizriazahmad-arch/onboarding-automation-system",
                "live_url": None,
                "icon_type": "cpu"
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
    except Exception as e:
        db.rollback()
        print(f"Error seeding projects: {e}")
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    """Run table creation, seeding, and startup audit logging cleanly."""
    try:
        models.Base.metadata.create_all(bind=engine)
        seed_projects()
        seed_settings()
        db = SessionLocal()
        try:
            create_audit_log_internal(db, "SYSTEM_STARTUP", "FastAPI application started and initialized database schemas.")
        finally:
            db.close()
    except Exception as err:
        print(f"Startup execution error: {err}")

# -----------------------------------------------------------------------------
# API Routes: Projects
# -----------------------------------------------------------------------------
@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Fetch all projects from the database."""
    try:
        projects = db.query(models.Project).all()
        return projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []

# -----------------------------------------------------------------------------
# API Routes: Approvals Workflow
# -----------------------------------------------------------------------------
@app.get("/api/approvals", response_model=List[schemas.ApprovalResponse])
def list_approvals(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch approval workflow requests with optional status filtering ('pending', 'approved', 'rejected')."""
    try:
        query = db.query(models.Approval)
        if status:
            query = query.filter(models.Approval.status == status.lower())
        return query.order_by(models.Approval.created_at.desc()).all()
    except Exception as e:
        print(f"Error fetching approvals: {e}")
        raise HTTPException(status_code=500, detail="Database query failed while fetching approvals.")

@app.post("/api/approvals", response_model=schemas.ApprovalResponse, status_code=status.HTTP_201_CREATED)
def create_approval(approval: schemas.ApprovalCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new approval workflow request."""
    try:
        db_approval = models.Approval(
            title=approval.title,
            description=approval.description,
            status="pending",
            requester=approval.requester,
            approver=approval.approver
        )
        db.add(db_approval)
        db.commit()
        db.refresh(db_approval)

        client_ip = request.client.host if request.client else "unknown"
        create_audit_log_internal(db, "APPROVAL_CREATED", f"Approval '{approval.title}' created by {approval.requester}", client_ip)
        return db_approval
    except Exception as e:
        db.rollback()
        print(f"Error creating approval: {e}")
        raise HTTPException(status_code=500, detail="Failed to create approval request.")

@app.get("/api/approvals/{approval_id}", response_model=schemas.ApprovalResponse)
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a specific approval request by ID."""
    db_approval = db.query(models.Approval).filter(models.Approval.id == approval_id).first()
    if not db_approval:
        raise HTTPException(status_code=404, detail=f"Approval with ID {approval_id} not found.")
    return db_approval

@app.patch("/api/approvals/{approval_id}", response_model=schemas.ApprovalResponse)
def update_approval(approval_id: int, update_data: schemas.ApprovalUpdate, request: Request, db: Session = Depends(get_db)):
    """Update approval status (approve/reject), approver, or comments."""
    db_approval = db.query(models.Approval).filter(models.Approval.id == approval_id).first()
    if not db_approval:
        raise HTTPException(status_code=404, detail=f"Approval with ID {approval_id} not found.")

    try:
        if update_data.status:
            valid_statuses = ["pending", "approved", "rejected"]
            if update_data.status.lower() not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
            db_approval.status = update_data.status.lower()

        if update_data.approver is not None:
            db_approval.approver = update_data.approver
        if update_data.comments is not None:
            db_approval.comments = update_data.comments

        db.commit()
        db.refresh(db_approval)

        client_ip = request.client.host if request.client else "unknown"
        create_audit_log_internal(
            db,
            "APPROVAL_UPDATED",
            f"Approval #{approval_id} status updated to '{db_approval.status}' by {db_approval.approver or 'system'}",
            client_ip
        )
        return db_approval
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating approval #{approval_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update approval request.")

@app.delete("/api/approvals/{approval_id}", status_code=status.HTTP_200_OK)
def delete_approval(approval_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete an approval record."""
    db_approval = db.query(models.Approval).filter(models.Approval.id == approval_id).first()
    if not db_approval:
        raise HTTPException(status_code=404, detail=f"Approval with ID {approval_id} not found.")

    try:
        db.delete(db_approval)
        db.commit()
        client_ip = request.client.host if request.client else "unknown"
        create_audit_log_internal(db, "APPROVAL_DELETED", f"Deleted approval #{approval_id}", client_ip)
        return {"detail": f"Approval #{approval_id} deleted successfully."}
    except Exception as e:
        db.rollback()
        print(f"Error deleting approval #{approval_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete approval request.")

# -----------------------------------------------------------------------------
# API Routes: Contact & Webhook
# -----------------------------------------------------------------------------
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
def submit_contact_form(message: schemas.ContactRequest, request: Request, db: Session = Depends(get_db)):
    """Save contact form message to the database, forward to Webhook, and record audit log."""
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

        # Forward payload to Webhook
        forward_lead_to_webhook(message.name, message.email, message.subject, message.message)

        # Audit log
        client_ip = request.client.host if request.client else "unknown"
        create_audit_log_internal(db, "CONTACT_FORM_SUBMITTED", f"From: {message.name} ({message.email})", client_ip)

        return db_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving your message: {str(e)}"
        )

# -----------------------------------------------------------------------------
# API Routes: AI Chatbot
# -----------------------------------------------------------------------------
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

@app.post("/api/chat")
async def handle_chat_message(request_data: schemas.ChatRequest, http_req: Request, db: Session = Depends(get_db)):
    """Handle chat messages with ultra-fast streaming Gemini AI (max_output_tokens=300, temperature=0.4, last 6 messages context)."""
    if not request_data.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    lead_captured = False
    name_extracted, email_extracted = extract_lead_info_from_messages(request_data.messages)
    if request_data.name:
        name_extracted = request_data.name.strip()
    if request_data.email:
        email_extracted = request_data.email.strip()

    if email_extracted and name_extracted:
        try:
            existing_lead = db.query(models.ContactMessage).filter(
                models.ContactMessage.email == email_extracted,
                models.ContactMessage.subject == "HR Autonomous Lead"
            ).first()

            if not existing_lead:
                conversation_transcript = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in request_data.messages])
                db_msg = models.ContactMessage(
                    name=name_extracted,
                    email=email_extracted,
                    subject="HR Autonomous Lead",
                    message=f"Chat Transcript:\n{conversation_transcript}"
                )
                db.add(db_msg)
                db.commit()

                forward_lead_to_webhook(
                    name=name_extracted,
                    email=email_extracted,
                    subject="HR Autonomous Lead",
                    message=conversation_transcript
                )
                client_ip = http_req.client.host if http_req.client else "unknown"
                create_audit_log_internal(db, "CHAT_LEAD_CAPTURED", f"Captured lead: {name_extracted} ({email_extracted})", client_ip)
                lead_captured = True
        except Exception as e:
            print(f"Error executing chat lead capture: {e}")

    # Human Greeting Short-Circuit logic (ONLY on initial message turn)
    last_user_msg = request_data.messages[-1].content.strip().lower()
    clean_last_msg = re.sub(r'[^\w\s]', '', last_user_msg).strip()

    greeting_responses = {
        "hi": "Hi 👋 What are you working on at the moment?",
        "hello": "Hey, welcome. What brings you here today?",
        "hey": "Good to have you here. What are you trying to improve or build right now?",
        "hey there": "Good to have you here. What are you trying to improve or build right now?",
        "hi there": "Hi 👋 What are you working on at the moment?",
        "good morning": "Good morning 👋 What project or workflow are you looking to build right now?",
        "good afternoon": "Good afternoon 👋 What project or workflow are you looking to build right now?",
        "good evening": "Good evening 👋 What project or workflow are you looking to build right now?",
        "yo": "Hey 👋 What are you working on right now?"
    }

    if len(request_data.messages) <= 1 and clean_last_msg in greeting_responses:
        async def greeting_stream():
            yield greeting_responses[clean_last_msg]
        return StreamingResponse(greeting_stream(), media_type="text/plain")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "PLACE_YOUR_KEY_HERE":
        async def offline_stream():
            yield "Connections are a bit busy right now, please try again in a moment or leave a message."
        return StreamingResponse(offline_stream(), media_type="text/plain")

    # Pass last 16 messages for full multi-turn context memory window
    history_context = []
    for msg in request_data.messages[-16:]:
        role_label = "Visitor" if msg.role == "user" else "HR Autonomous Specialist"
        history_context.append(f"{role_label}: {msg.content}")

    full_prompt = f"System Persona & Directives:\n{SYSTEM_PROMPT}\n\nFull Conversation History:\n" + "\n".join(history_context) + "\n\nHR Autonomous Specialist:"
    target_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash"]

    async def stream_generator():
        streamed_any = False
        accumulated_text = ""

        # 1. Attempt Modern google.genai Client SDK streaming
        if GENAI_CLIENT is not None:
            for m_name in target_models:
                try:
                    def get_sdk_stream(m=m_name):
                        return GENAI_CLIENT.models.generate_content_stream(
                            model=m,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(
                                max_output_tokens=300,
                                temperature=0.4
                            )
                        )
                    
                    sdk_stream = await asyncio.to_thread(get_sdk_stream)
                    for chunk in sdk_stream:
                        if chunk and chunk.text:
                            accumulated_text += chunk.text
                    if accumulated_text:
                        streamed_any = True
                        sanitized = sanitize_consultant_response(accumulated_text)
                        yield sanitized
                        return
                except Exception as client_err:
                    print(f"Modern google.genai SDK streaming failed for {m_name}: {client_err}")

        # 2. Fallback to Legacy SDK
        if not streamed_any and LEGACY_GENAI is not None:
            for m_name in target_models:
                try:
                    def get_legacy_resp(m=m_name):
                        gen_model = LEGACY_GENAI.GenerativeModel(
                            model_name=m,
                            system_instruction=SYSTEM_PROMPT,
                            generation_config={"max_output_tokens": 300, "temperature": 0.4}
                        )
                        return gen_model.generate_content(full_prompt)

                    legacy_res = await asyncio.to_thread(get_legacy_resp)
                    if legacy_res and legacy_res.text:
                        streamed_any = True
                        sanitized = sanitize_consultant_response(legacy_res.text.strip())
                        yield sanitized
                        return
                except Exception as sdk_err:
                    print(f"Legacy SDK failed for {m_name}: {sdk_err}")

        # 3. Fallback to Direct REST API Call
        if not streamed_any:
            for model_name in target_models:
                try:
                    def get_rest_resp(m=model_name):
                        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                        payload = json.dumps({
                            "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
                            "generationConfig": {"maxOutputTokens": 300, "temperature": 0.4}
                        }).encode("utf-8")
                        req = urllib.request.Request(gemini_url, data=payload, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            result = json.loads(resp.read().decode("utf-8"))
                            candidates = result.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts:
                                    return parts[0].get("text", "").strip()
                        return None

                    rest_reply = await asyncio.to_thread(get_rest_resp)
                    if rest_reply:
                        streamed_any = True
                        sanitized = sanitize_consultant_response(rest_reply)
                        yield sanitized
                        return
                except Exception as endpoint_err:
                    print(f"REST API failed for {model_name}: {endpoint_err}")

        if not streamed_any:
            yield "Connections are a bit busy right now, please try again in a moment or leave a message."

    return StreamingResponse(stream_generator(), media_type="text/plain")

# -----------------------------------------------------------------------------
# API Routes: Settings
# -----------------------------------------------------------------------------
@app.get("/api/settings", response_model=List[schemas.SettingResponse])
def get_settings(db: Session = Depends(get_db)):
    """Fetch all application settings."""
    try:
        return db.query(models.Setting).all()
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return []

@app.put("/api/settings/{key}", response_model=schemas.SettingResponse)
def update_setting(key: str, update: schemas.SettingUpdate, request: Request, db: Session = Depends(get_db)):
    """Update a specific setting by key."""
    setting = db.query(models.Setting).filter_by(key=key).first()
    if not setting:
        setting = models.Setting(key=key, value=update.value, description=update.description)
        db.add(setting)
    else:
        setting.value = update.value
        if update.description is not None:
            setting.description = update.description

    db.commit()
    db.refresh(setting)

    client_ip = request.client.host if request.client else "unknown"
    create_audit_log_internal(db, "SETTING_UPDATED", f"Key: {key} = {update.value}", client_ip)
    return setting

# -----------------------------------------------------------------------------
# API Routes: CRM & System Status
# -----------------------------------------------------------------------------
@app.get("/api/crm/status", response_model=schemas.CRMStatusResponse)
def get_crm_status(db: Session = Depends(get_db)):
    """Get system and CRM operational status."""
    try:
        total_messages = db.query(models.ContactMessage).count()
        total_projects = db.query(models.Project).count()
        total_logs = db.query(models.AuditLog).count()

        last_msg = db.query(models.ContactMessage).order_by(models.ContactMessage.created_at.desc()).first()
        last_activity = last_msg.created_at if last_msg else None

        webhook_url = os.getenv("GOOGLE_APPS_SCRIPT_WEBHOOK_URL")
        has_webhook = bool(webhook_url and webhook_url != "PLACE_HOLDER")

        api_key = os.getenv("GEMINI_API_KEY")
        gemini_status = "operational" if (api_key and api_key != "PLACE_YOUR_KEY_HERE") else "unconfigured"

        return schemas.CRMStatusResponse(
            system_status="online",
            total_contact_messages=total_messages,
            total_projects=total_projects,
            total_audit_logs=total_logs,
            webhook_configured=has_webhook,
            gemini_ai_status=gemini_status,
            last_activity=last_activity
        )
    except Exception as e:
        print(f"Error fetching CRM status: {e}")
        return schemas.CRMStatusResponse(
            system_status="degraded",
            total_contact_messages=0,
            total_projects=0,
            total_audit_logs=0,
            webhook_configured=False,
            gemini_ai_status="error",
            last_activity=None
        )

# -----------------------------------------------------------------------------
# API Routes: Audit Logs
# -----------------------------------------------------------------------------
@app.get("/api/audit-logs", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch system audit logs."""
    try:
        return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(limit).all()
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return []

@app.post("/api/audit-logs", response_model=schemas.AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log_endpoint(log_data: schemas.AuditLogCreate, request: Request, db: Session = Depends(get_db)):
    """Create a manual audit log entry."""
    client_ip = log_data.ip_address or (request.client.host if request.client else "unknown")
    entry = create_audit_log_internal(db, log_data.action, log_data.details, client_ip)
    if not entry:
        raise HTTPException(status_code=500, detail="Failed to create audit log")
    return entry

# -----------------------------------------------------------------------------
# Serve Static Frontend
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
