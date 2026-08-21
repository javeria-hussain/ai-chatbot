from fastapi import FastAPI
from app.api.v1.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1 import leads
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="MoinSystems AI Chatbot")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1", tags=["leads"])


ALLOWED_ORIGINS = [
    "https://www.moinsystemsai.com",
    "https://moinsystemsai.com",
]
if settings.ENVIRONMENT != "production":
    ALLOWED_ORIGINS.append("http://localhost:3000")  

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
