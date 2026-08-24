from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import ChatSession, LeadSubmission
from app.schemas.lead import LeadCaptureRequest, LeadCaptureResponse
from app.leads.validators import validate_field
from app.leads.lead_service import get_draft_lead, create_draft_lead
from app.leads.notification_service import send_lead_notification
from app.leads.notification_service import send_lead_notification
router = APIRouter()


@router.post("/lead-capture", response_model=LeadCaptureResponse)
async def submit_lead(payload: LeadCaptureRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).where(ChatSession.session_token == payload.session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    errors = {}
    for field in ("name", "email", "phone"):
        error = validate_field(field, getattr(payload, field))
        if error:
            errors[field] = error

    if errors:
        return LeadCaptureResponse(success=False, status="invalid", errors=errors)

    lead = await get_draft_lead(db, session.id)
    if lead is None:
        lead = await create_draft_lead(db, session.id)

    lead.name = payload.name.strip()
    lead.email = payload.email.strip()
    lead.phone = payload.phone.strip()
    lead.message = payload.message
    lead.status = "complete"
    await db.commit()

    notification_result = await send_lead_notification(db, session, lead)

    return LeadCaptureResponse(success=True, status="complete")
