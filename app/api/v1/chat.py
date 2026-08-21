from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.history import get_or_create_session, get_recent_history, save_message
from app.chat.intent_service import detect_intent
from app.chat.orchestrator import ChatOrchestrator
from app.core.limiter import limiter
from app.db.session import get_db
from app.leads.lead_service import (
    create_draft_lead,
    finalize_if_complete,
    get_draft_lead,
    missing_fields,
    next_missing_field,
    update_lead_field,
)
from app.leads.validators import validate_field
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse

LEAD_TRIGGER_INTENTS = {"pricing_quote", "buying_intent"}

router = APIRouter(prefix="/chat", tags=["chat"])
orchestrator = ChatOrchestrator()


@router.post("/messages", response_model=ChatMessageResponse)
@limiter.limit("10/minute")
async def send_message(
    request: Request,
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    session = await get_or_create_session(db, payload.session_id)
    history = await get_recent_history(db, session.id)

    intent = detect_intent(payload.message)
    await save_message(
        db, session.id, role="user", content=payload.message, intent=intent
    )

    from app.leads.validators import validate_field
    from app.leads.notification_service import send_lead_notification

    lead = await get_draft_lead(db, session.id)
    lead_newly_created = False
    field_error = None
    just_completed = False

    if lead is None and intent in LEAD_TRIGGER_INTENTS:
        lead = await create_draft_lead(db, session.id)
        lead_newly_created = True

    if lead and not lead_newly_created:
        field = next_missing_field(lead)
        if field:
            field_error = validate_field(field, payload.message)
            if field_error is None:
                await update_lead_field(db, lead, field, payload.message)
                just_completed = await finalize_if_complete(db, lead)

    notification_sent = False
    if just_completed:
        notify_result = await send_lead_notification(db, session, lead)
        notification_sent = notify_result.success

    if lead:
        missing = missing_fields(lead)
        lead_capture_required = len(missing) > 0
    else:
        missing = []
        lead_capture_required = False

    try:
        result = await orchestrator.get_response(
            db=db,
            user_message=payload.message,
            chat_history=history,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {e}")

    answer = result["answer"]
    if just_completed:
        if notification_sent:
            answer = (
                "Thank you! Your details have been submitted — our team will get back to you soon.\n\n"
                + answer
            )
        else:
            answer = (
                "Thanks for the details — we've saved them, and our team will follow up soon.\n\n"
                + answer
            )

    await save_message(db, session.id, role="assistant", content=answer)
    await db.commit()

    return ChatMessageResponse(
        session_id=session.session_token,
        answer=answer,
        sources_used=result["sources_used"],
        grounded=result["grounded"],
        lead_capture_required=lead_capture_required,
        missing_lead_fields=missing,
        field_validation_error=field_error,
        lead_submitted=just_completed,
        notification_sent=notification_sent,
    )
