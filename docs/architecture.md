# Architecture

- **Frontend**: Vite/React consuming REST endpoints from FastAPI. Env: `VITE_API_BASE`.
- **Backend**: FastAPI (Python 3.11), SQLite default. Authentication via JWT. Endpoints include `/auth/*`, `/jobs`, `/jobs/search`, `/upload/resume`, `/assistant/chat`.
- **AI**: OpenAI Chat Completions with minimal system prompt "Penguin".
- **Jobs ingestion**: Adapter pattern (cron) for future real sources.

Key envs in `.env.example`. See the README quickstart.
