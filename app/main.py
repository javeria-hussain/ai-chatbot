import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import leads
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.sessions import router as sessions_router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging_config import logger, setup_logging

setup_logging()

MAX_REQUEST_BODY_SIZE = 10 * 1024

app = FastAPI(title="MoinSystems AI Chatbot")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = [
    "https://www.moinsystemsai.com",
    "https://moinsystemsai.com",
]
if settings.environment != "production":
    ALLOWED_ORIGINS.append("http://localhost:3000")
    ALLOWED_ORIGINS.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
        return JSONResponse(
            status_code=413, content={"detail": "Request body too large"}
        )
    return await call_next(request)


app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1", tags=["leads"])

@app.get("/")
def read_root():
    return {"status": "online", "message": "FastAPI AI Chatbot is running on Vercel!"}