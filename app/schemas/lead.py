from pydantic import BaseModel, Field
from uuid import UUID


class LeadCaptureRequest(BaseModel):
    session_id: UUID
    name: str = Field(..., min_length=2)
    email: str
    phone: str
    message: str | None = None


class LeadCaptureResponse(BaseModel):
    success: bool
    status: str
    errors: dict[str, str] = {}