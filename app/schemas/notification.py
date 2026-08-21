from datetime import datetime
from pydantic import BaseModel


class NotificationPayload(BaseModel):
    name: str | None = None
    email: str | None = None
    contact_number: str | None = None
    company: str | None = None
    user_question: str | None = None
    service_interest: str | None = None
    project_summary: str | None = None
    timeline_budget: str | None = None
    source_page: str | None = None
    conversation_summary: str
    timestamp: datetime
