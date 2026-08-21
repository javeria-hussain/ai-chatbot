from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from app.db.base import Base

class ChatSession(Base):
    __tablename__ = "chat_session"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_token: Mapped[uuid.UUID] = mapped_column(unique=True, index=True, default=uuid.uuid4)
    source_page: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_activity_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_message"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class LeadSubmission(Base):
    __tablename__ = "lead_submission"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_session.id"))
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    service_interest: Mapped[str | None] = mapped_column(String, nullable=True)
    project_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline_budget: Mapped[str | None] = mapped_column(String, nullable=True)

class EmailNotification(Base):
    __tablename__ = "email_notification"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lead_submission.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    provider_message_id: Mapped[str | None] = mapped_column(String, nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_document"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)  
    title: Mapped[str] = mapped_column(String(300))
    source: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunk"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)  
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_document.id"))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    intents: Mapped[str | None] = mapped_column(String(300), nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(384))   
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
