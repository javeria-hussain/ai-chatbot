# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="local", env="APP_ENV")
    database_url: str = Field(..., env="DATABASE_URL")
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
    allowed_origins: str = Field(default="http://localhost:3000", env="ALLOWED_ORIGINS")
    app_secret: str = Field(default="", env="APP_SECRET")
    embedding_dim: int = Field(default=384, env="EMBEDDING_DIM")
    rag_top_k: int = Field(default=5, env="RAG_TOP_K")
    rag_similarity_threshold: float = Field(
        default=0.35, env="RAG_SIMILARITY_THRESHOLD"
    )
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    llm_model: str = Field(default="llama-3.3-70b-versatile", env="LLM_MODEL")
    resend_api_key: str = Field(..., env="RESEND_API_KEY")
    notification_from_email: str = Field(..., env="NOTIFICATION_FROM_EMAIL")
    notification_to_email: str = Field(..., env="NOTIFICATION_TO_EMAIL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")

    # ✅ Sirf yeh rakhein - NO env_file!
    model_config = {"case_sensitive": False, "extra": "ignore"}


settings = Settings()
