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


async def get_lead_for_session(
    db: AsyncSession, session_id: UUID
) -> LeadSubmission | None:
    result = await db.execute(
        select(LeadSubmission)
        .where(LeadSubmission.session_id == session_id)
        .order_by(LeadSubmission.created_at.desc())
    )
    return result.scalars().first()


import re
from app.leads.validators import validate_field

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-().]{6,}\d)")
NAME_PATTERNS = [
    re.compile(
        r"(?:my name is|i am|i'm|this is|name[:\s]+)\s*([a-zA-Z][a-zA-Z\s.'-]{1,40})",
        re.I,
    ),
]


async def try_extract_and_update(
    db: AsyncSession,
    lead: LeadSubmission,
    message: str,
) -> tuple[list[str], str | None, bool]:
    """
    Try to pull name / email / phone from free-text message.
    Returns (still_missing, field_error, just_completed).
    """
    text = message.strip()
    field_error = None
    updated_any = False

    # 1. Email
    if not lead.email:
        m = EMAIL_RE.search(text)
        if m:
            err = validate_field("email", m.group(0))
            if err:
                field_error = err
            else:
                await update_lead_field(db, lead, "email", m.group(0))
                updated_any = True

    # 2. Phone
    if not lead.phone:
        m = PHONE_RE.search(text)
        if m:
            digits = re.sub(r"[^\d]", "", m.group(0))
            if len(digits) >= 7:
                err = validate_field("phone", m.group(0))
                if err:
                    field_error = err
                else:
                    await update_lead_field(db, lead, "phone", m.group(0))
                    updated_any = True

    # 3. Name (patterns first, then whole-message fallback if only name missing)
    if not lead.name:
        name_val = None
        for pat in NAME_PATTERNS:
            m = pat.search(text)
            if m:
                name_val = m.group(1).strip()
                break
        # sequential fallback: pure short text when name is the only missing field
        if name_val is None and next_missing_field(lead) == "name":
            cleaned = re.sub(r"[^a-zA-Z\s.'-]", "", text).strip()
            if (
                2 <= len(cleaned) <= 40
                and not EMAIL_RE.search(text)
                and not PHONE_RE.search(text)
            ):
                name_val = cleaned

        if name_val:
            err = validate_field("name", name_val)
            if err:
                field_error = err
            else:
                await update_lead_field(db, lead, "name", name_val)
                updated_any = True

        still_missing = missing_fields(lead)
    just_completed = False
    if not still_missing:
        just_completed = await finalize_if_complete(db, lead)

    return still_missing, field_error, just_completed
