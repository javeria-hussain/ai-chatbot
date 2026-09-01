# MoinSystems AI Chatbot

An AI-powered chatbot backend for the MoinSystems website. It answers visitor questions using a RAG (Retrieval-Augmented Generation) pipeline, and captures leads (name/email/phone) from interested visitors, sending an email notification to the team.

**Live API:** https://ai-chatbot-production-fa10.up.railway.app/
**API Docs:** https://ai-chatbot-production-fa10.up.railway.app/docs

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Database:** PostgreSQL + pgvector (hosted on Neon)
- **ORM:** SQLAlchemy (async) + Alembic for migrations
- **LLM:** Groq (llama-3.3-70b-versatile)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2), vendored locally
- **Email:** Resend
- **Frontend widget:** React + TypeScript
- **Hosting:** Railway

## Getting Started

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/javeria-hussain/ai-chatbot
cd ai-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own values (see **Environment Variables** below).

Run the server locally:

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` to try the API.

## Environment Variables

| Variable | What it's for |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `LLM_PROVIDER` | LLM provider, e.g. `groq` |
| `GROQ_API_KEY` | Your Groq API key |
| `LLM_MODEL` | Which model to use |
| `EMBEDDING_MODEL` | Path to the local embedding model |
| `EMBEDDING_DIM` | Embedding vector size |
| `RAG_SIMILARITY_THRESHOLD` | Minimum similarity score for RAG matches |
| `RESEND_API_KEY` | Your Resend API key |
| `NOTIFICATION_FROM_EMAIL` | Sender address for lead emails |
| `NOTIFICATION_TO_EMAIL` | Where lead notifications go |
| `APP_SECRET` | App secret key |
| `ALLOWED_ORIGINS` | Which domains can call this API (CORS) |

No real values are stored here — keep them in your own `.env` file, never commit it.

## Main API Endpoints

- `GET /api/v1/health` — check if the service is up
- `POST /api/v1/session` — start a chat session
- `POST /api/v1/chat/messages` — send a message, get a reply
- `POST /api/v1/lead` — submit a lead
- `GET /docs` — full interactive API documentation

## Running Tests

```bash
pytest
```

## Deployment Notes

- Deployed on Railway (build command, start command, and pre-deploy migration command are set in Railway's project settings).
- The embedding model is stored directly in the `models/` folder in this repo, not downloaded at runtime — Railway blocks outbound calls during build/runtime, so this avoids that issue.
- The frontend widget is a separate static bundle meant to be hosted on the main website, not part of this backend deployment.