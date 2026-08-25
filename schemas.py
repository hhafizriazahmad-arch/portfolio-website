from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    tech_stack: str
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    icon_type: str

    class Config:
        from_attributes = True

class ContactRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

ContactMessageCreate = ContactRequest

class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    name: Optional[str] = None
    email: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    lead_captured: bool = False
    prompt_lead_capture: bool = False

class SettingResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None

class CRMStatusResponse(BaseModel):
    system_status: str
    total_contact_messages: int
    total_projects: int
    total_audit_logs: int
    webhook_configured: bool
    gemini_ai_status: str
    last_activity: Optional[datetime] = None

class AuditLogCreate(BaseModel):
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ApprovalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    requester: str
    approver: Optional[str] = None

class ApprovalUpdate(BaseModel):
    status: Optional[str] = None  # "pending", "approved", "rejected"
    approver: Optional[str] = None
    comments: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    requester: str
    approver: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


