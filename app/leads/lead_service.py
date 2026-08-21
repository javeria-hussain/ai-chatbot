from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.models import LeadSubmission

REQUIRED_LEAD_FIELDS = ["name", "email", "phone"]


async def get_draft_lead(db: AsyncSession, session_id: UUID) -> LeadSubmission | None:
    result = await db.execute(
        select(LeadSubmission).where(
            LeadSubmission.session_id == session_id,
            LeadSubmission.status == "draft",
        )
    )
    return result.scalar_one_or_none()


async def create_draft_lead(db: AsyncSession, session_id: UUID) -> LeadSubmission:
    lead = LeadSubmission(session_id=session_id, status="draft")
    db.add(lead)
    await db.flush()
    return lead


def missing_fields(lead: LeadSubmission) -> list[str]:
    return [field for field in REQUIRED_LEAD_FIELDS if not getattr(lead, field)]


def next_missing_field(lead: LeadSubmission) -> str | None:
    missing = missing_fields(lead)
    return missing[0] if missing else None


async def update_lead_field(db: AsyncSession, lead: LeadSubmission, field: str, value: str) -> LeadSubmission:
    setattr(lead, field, value.strip())
    await db.flush()
    return lead

async def finalize_if_complete(db: AsyncSession, lead: LeadSubmission) -> bool:
    if not missing_fields(lead):
        lead.status = "complete"
        await db.flush()
        return True
    return False

async def finalize_if_complete(db: AsyncSession, lead: LeadSubmission) -> bool:
    if not missing_fields(lead):
        lead.status = "complete"
        await db.flush()
        return True
    return False