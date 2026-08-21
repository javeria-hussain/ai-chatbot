from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SessionCreateRequest(BaseModel):
    source_page: str | None = None


class SessionResponse(BaseModel):
    session_id: UUID
    status: str
    started_at: datetime

    class Config:
        from_attributes = True
