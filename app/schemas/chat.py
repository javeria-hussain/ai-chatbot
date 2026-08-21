from pydantic import BaseModel, Field
from uuid import UUID


class ChatMessageRequest(BaseModel):
    session_id: UUID | None = None
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    session_id: UUID
    answer: str
    sources_used: int
    grounded: bool
    lead_capture_required: bool = False
    missing_lead_fields: list[str] = []
    field_validation_error: str | None = None
    lead_submitted: bool = False
    notification_sent: bool = False
