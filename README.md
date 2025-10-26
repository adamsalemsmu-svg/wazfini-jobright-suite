# wazfini-jobright-suite

> UAE-focused job search and AI copilot app with resume parsing, near-realtime job ingestion, and a clean, advanced UI.

[![Build](https://img.shields.io/github/actions/workflow/status/adamsalemsmu-svg/wazfini-jobright-suite/ci.yml)](https://github.com/adamsalemsmu-svg/wazfini-jobright-suite/actions)
[![Version](https://img.shields.io/github/v/tag/adamsalemsmu-svg/wazfini-jobright-suite)](https://github.com/adamsalemsmu-svg/wazfini-jobright-suite/releases)
[![License](https://img.shields.io/github/license/adamsalemsmu-svg/wazfini-jobright-suite)](LICENSE)

## Quickstart

```bash
# Clone
git clone https://github.com/adamsalemsmu-svg/wazfini-jobright-suite.git
cd wazfini-jobright-suite

# Copy envs
cp .env.example .env

# Bootstrap dev
./scripts/bootstrap.sh         # Windows: scripts\bootstrap.ps1
./scripts/dev.sh               # or: make dev
```

### Environment Variables

| Name | Required | Default | Description |
| --- | ---: | --- | --- |
| APP_ENV | no | `local` | Deployment environment label (local/staging/prod) |
| BASE_URL | no | `http://127.0.0.1:8000` | Public URL for backend, used in emails and smoke tests |
| SECRET_KEY | yes | — | 32+ char secret for JWT signing and security tokens |
| JWT_ALGORITHM | no | `HS256` | JWT signing algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | no | `15` | Access token lifetime in minutes |
| REFRESH_TOKEN_EXPIRE_DAYS | no | `15` | Refresh token lifetime in days |
| DATABASE_URL | yes | `sqlite:///./app.db` | SQLAlchemy database URL (Postgres in prod) |
| REDIS_URL | yes | `redis://localhost:6379/0` | Redis connection string for login guard + token store |
| EMAIL_SENDER | yes | — | From address for transactional emails |
| SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS | yes* | — | SMTP credentials for password reset email (skip to log-only mode) |
| LOG_LEVEL | no | `INFO` | Application log level |
| SENTRY_DSN | no | — | Optional error reporting DSN |
| CORS_ALLOW_ORIGINS | no | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed front-end origins |
| OPENAI_API_KEY | optional | — | Enables Penguin assistant responses |
| OPENAI_MODEL | optional | `gpt-4o-mini` | OpenAI chat model |
| VITE_API_BASE | yes | `http://127.0.0.1:8000` | Frontend API base URL |

\* If SMTP credentials are omitted, password reset emails are logged but not delivered.

### Tech Stack
Python FastAPI + SQLite + Vite/React (Node 20, Python 3.11).

### Architecture (ASCII)
```
+-------------+        HTTP        +------------------+
|  Frontend   | <----------------> |  FastAPI Backend |
| Vite/React  |                    |  SQLite + Jobs   |
+-------------+                    +------------------+
       |                                   |
       | resume upload                     | resume parser
       |---------------------------------->|
       |                                   |
       | Penguin chat                      | OpenAI API
       |---------------------------------->+----->
```

See `docs/architecture.md` and `docs/roadmap.md` for details.

### Scripts

- `scripts/bootstrap.(sh|ps1)` — install toolchains, deps, pre-commit
- `scripts/dev.(sh|ps1)` — run backend + frontend locally
- `scripts/test.(sh|ps1)` — run tests
- `scripts/verify.(sh|ps1)` — lint + type-check + tests
- `scripts/smoke.sh` — end-to-end staging smoke (`BASE_URL=https://api.example.com ./scripts/smoke.sh`)

### Database & Auth

- Run migrations: `cd backend && alembic upgrade head`
- Seed demo account: `PYTHONPATH=backend python scripts/seed.py`
- Password policy: min 10 characters with mixed character classes, or 16+ char passphrase
- Redis powers login rate limiting, refresh rotation, and password reset tokens

## License
MIT
