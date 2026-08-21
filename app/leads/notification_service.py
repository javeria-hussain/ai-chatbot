from app.core.config import settings
from app.email.resend_provider import ResendProvider
from app.email.templates import render_lead_notification
from app.leads.notification_builder import build_notification_payload
from app.email.base import EmailResult
from app.db.models import EmailNotification
from datetime import datetime, timezone


async def send_lead_notification(db, session, lead) -> EmailResult:
    payload = await build_notification_payload(db, session, lead)
    subject, html_body = render_lead_notification(payload)

    provider = ResendProvider()
    result = await provider.send_email(
        to=settings.NOTIFICATION_TO_EMAIL,
        subject=subject,
        html_body=html_body,
    )

    notification_row = EmailNotification(
        lead_id=lead.id,
        status="sent" if result.success else "failed",
        sent_at=(
            datetime.now(timezone.utc).replace(tzinfo=None) if result.success else None
        ),
        provider_message_id=result.provider_message_id,
        error_detail=result.error,
    )
    db.add(notification_row)
    await db.commit()

    return result
