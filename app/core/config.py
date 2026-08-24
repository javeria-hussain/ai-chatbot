# app/core/config.py
import os
from pydantic import BaseModel


class Settings(BaseModel):
    # App Settings
    app_env: str = os.getenv("APP_ENV", "local")
    environment: str = os.getenv("ENVIRONMENT", "development")
    app_secret: str = os.getenv("APP_SECRET", "")

    # Database - Required
    database_url: str = os.getenv("DATABASE_URL", "")

    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Embedding
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "384"))

    # RAG
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    rag_similarity_threshold: float = float(
        os.getenv("RAG_SIMILARITY_THRESHOLD", "0.35")
    )

    # CORS
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")

    # Email - Required
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    notification_from_email: str = os.getenv("NOTIFICATION_FROM_EMAIL", "")
    notification_to_email: str = os.getenv("NOTIFICATION_TO_EMAIL", "")

    def __init__(self, **data):
        super().__init__(**data)
        # Validate required fields
        missing = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if not self.resend_api_key:
            missing.append("RESEND_API_KEY")
        if not self.notification_from_email:
            missing.append("NOTIFICATION_FROM_EMAIL")
        if not self.notification_to_email:
            missing.append("NOTIFICATION_TO_EMAIL")

        if missing:
            raise ValueError(
                f"❌ Missing required environment variables: {', '.join(missing)}"
            )


# Create settings instance
settings = Settings()
