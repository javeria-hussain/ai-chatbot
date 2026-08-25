import asyncio
import resend
from app.core.config import settings
from app.email.base import EmailProvider, EmailResult

TRANSIENT_ERROR_KEYWORDS = ("timeout", "503", "502", "rate limit", "connection")
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.5


class ResendProvider(EmailProvider):
    def __init__(self):
        resend.api_key = settings.resend_api_key

    async def send_email(self, to: str, subject: str, html_body: str) -> EmailResult:
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = resend.Emails.send(
                    {
                        "from": settings.notification_from_email,
                        "to": [to],
                        "subject": subject,
                        "html": html_body,
                    }
                )
                return EmailResult(
                    success=True,
                    provider_message_id=response.get("id"),
                )
            except Exception as e:
                last_error = str(e)
                is_transient = any(
                    kw in last_error.lower() for kw in TRANSIENT_ERROR_KEYWORDS
                )
                if not is_transient or attempt == MAX_RETRIES:
                    break
                await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))

        return EmailResult(success=False, error=last_error)
