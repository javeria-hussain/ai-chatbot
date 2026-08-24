from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "local"
    database_url: str
    llm_provider: str = "openai"
    openai_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    anthropic_api_key: str = ""
    allowed_origins: str = "http://localhost:3000"
    app_secret: str = ""
    embedding_dim: int = 384
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.35
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    resend_api_key: str
    notification_from_email: str
    notification_to_email: str
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
