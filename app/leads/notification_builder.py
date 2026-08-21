from datetime import datetime, timezone

from app.chat.history import get_recent_history
from app.schemas.notification import NotificationPayload


async def build_notification_payload(db, session, lead) -> NotificationPayload:
    messages = await get_recent_history(db, session.id, limit=20)

    conversation_lines = [
    f"{m['role']}: {m['content']}" for m in messages
    ]
    conversation_summary = "\n".join(conversation_lines) or "No conversation recorded."

    last_user_message = next(
    (m["content"] for m in reversed(messages) if m["role"] == "user"), None
    )

    return NotificationPayload(
        name=lead.name,
        email=lead.email,
        contact_number=lead.phone,
        company=lead.company,
        user_question=last_user_message,
        service_interest=lead.service_interest,
        project_summary=lead.project_summary,
        timeline_budget=lead.timeline_budget,
        source_page=session.source_page,
        conversation_summary=conversation_summary,
        timestamp=datetime.now(timezone.utc),
    )
