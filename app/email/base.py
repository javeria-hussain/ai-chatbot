from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmailResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class EmailProvider(ABC):
    @abstractmethod
    async def send_email(
        self, to: str, subject: str, html_body: str
    ) -> EmailResult:
        ...