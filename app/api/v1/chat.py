import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.history import get_or_create_session, get_recent_history, save_message
from app.chat.intent_service import detect_intent
from app.chat.orchestrator import ChatOrchestrator
from app.core.limiter import limiter
from app.core.logging_config import logger
from app.db.session import get_db
from app.leads.lead_service import (
    create_draft_lead,
    get_lead_for_session,
    missing_fields,
    try_extract_and_update,
)
from app.leads.notification_service import send_lead_notification
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
    request_id = str(uuid.uuid4())
    start_time = time.time()

    session = await get_or_create_session(db, payload.session_id)
    history = await get_recent_history(db, session.id)

    intent = detect_intent(payload.message)
    await save_message(
        db, session.id, role="user", content=payload.message, intent=intent
    )

    lead = await get_lead_for_session(db, session.id)
    field_error = None
    just_completed = False
    notification_sent = False
    missing = []
    lead_capture_required = False

    from app.leads.lead_service import EMAIL_RE, PHONE_RE

    has_contact = bool(
        EMAIL_RE.search(payload.message) or PHONE_RE.search(payload.message)
    )
    if lead is None and (intent in LEAD_TRIGGER_INTENTS or has_contact):
        lead = await create_draft_lead(db, session.id)

    if lead and lead.status != "complete":
        missing, field_error, just_completed = await try_extract_and_update(
            db, lead, payload.message
        )
        lead_capture_required = len(missing) > 0

        if just_completed:
            try:
                await send_lead_notification(db,session, lead)
                notification_sent = True
            except Exception as e:
                logger.error(f"Lead notification failed: {e}")
                notification_sent = False

    try:
        result = await orchestrator.get_response(
            db=db,
            user_message=payload.message,
            chat_history=history,
            lead_already_captured=(lead is not None and lead.status == "complete"),
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

    latency_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"request_id={request_id} latency_ms={latency_ms} "
        f"intent={intent} sources_used={result['sources_used']} "
        f"grounded={result['grounded']} lead_submitted={just_completed} "
        f"notification_sent={notification_sent}"
    )

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
