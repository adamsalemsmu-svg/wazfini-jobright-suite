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
|---|---:|---|---|
| OPENAI_API_KEY | yes | — | OpenAI key for Penguin assistant |
| DATABASE_URL | no | sqlite:///./app/data/wazfini.db | DB connection string |
| CORS_ALLOW_ORIGINS | no | http://localhost:5173,http://127.0.0.1:5173 | Allowed origins |
| VITE_API_BASE | yes | http://127.0.0.1:8000 | Backend API endpoint |

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

## License
MIT
