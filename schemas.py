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
