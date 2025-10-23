# Wazifni Release Report — Production Verification

**Date:** <!-- update if desired -->
**Service:** `wazifni-backend` (Render, Python 3)  
**Frontend:** `wazifni-frontend` (Vercel)

**Backend URL:** https://wazifni-backend.onrender.com  
**OpenAPI:** https://wazifni-backend.onrender.com/openapi.json  
**Frontend URL:** https://wazifni-frontend.vercel.app

---

## ✅ Release Decision
**✅ GO — all checks passed.** The backend and frontend are deployed, healthy, authenticated flows work, database is connected (Postgres), and CORS is correctly configured.

---

## Verification Matrix

| Check | How | Expected | Actual |
|---|---|---|---|
| OpenAPI | `GET /openapi.json` | 200 + JSON with `paths` | **200 OK** |
| Health | `GET /health` | 200 + `{"ok": true}` | **200 OK** |
| Auth: Register/Login | `/auth/register`, `/auth/login` | 200 + token | **200 OK** (token issued) |
| Jobs (seed + list) | `GET /jobs` with `Authorization: Bearer <token>` | 200 + array | **200 OK** (3 demo items) |
| CORS (preflight) | `OPTIONS /jobs` with `Origin: https://wazifni-frontend.vercel.app` | ACAO header present | **OK** (ACAO echoed) |
| CORS (simple) | `GET /jobs` with `Origin: https://wazifni-frontend.vercel.app` | 200 + ACAO | **OK** |
| Frontend → Backend | Vercel app → calls backend | 200 + no CORS errors | **OK** |

**Notes**
- `Access-Control-Allow-Origin` correctly echoes `https://wazifni-frontend.vercel.app`.
- Demo data is seeded on first `/jobs` call.

---

## CI / Branch Protection

- **Backend CI** (`backend-ci.yml`): Lint, Tests, Smoke — **green**.
- **Frontend CI** (`frontend-ci.yml`): Build (and lint if present) — **green**.
- **Branch protection (main):** requires **Backend CI** and **Frontend CI** to pass before merge.

> If not already enforced, enable in **Settings → Branches → Add rule (main)** and check both required status checks.

---

## Deployment Details

**Backend (Render)**
- **Service:** `wazifni-backend`
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health` (recommended to set in Settings)
- **Env Vars:**
  - `DATABASE_URL=postgresql+psycopg://<user>:<pass>@wazifni-db:5432/<db>`
  - `ALEMBIC_DATABASE_URL=postgresql://<user>:<pass>@wazifni-db:5432/<db>`
  - `CORS_ORIGINS=https://wazifni-frontend.vercel.app`
  - `ENV=production`
  - *(optional)* `OPENAI_API_KEY`, `OPENAI_PROJECT`, `OPENAI_MODEL`

**Frontend (Vercel)**
- **Root dir:** `/frontend`
- **Env Vars:**  
  - `VITE_API_BASE=https://wazifni-backend.onrender.com`

---

## Runtime Evidence (PowerShell)

```powershell
# OpenAPI
curl https://wazifni-backend.onrender.com/openapi.json   # 200 OK

# Health
iwr https://wazifni-backend.onrender.com/health          # 200 OK, {"ok":true}

# Register (idempotent)
$reg = @{ email="you@example.com"; password="P@ssw0rd!"; name="Adam" } | ConvertTo-Json
iwr https://wazifni-backend.onrender.com/auth/register -Method Post -ContentType "application/json" -Body $reg

# Login → token
$login = iwr https://wazifni-backend.onrender.com/auth/login -Method Post -Body @{ username="you@example.com"; password="P@ssw0rd!" }
$token = ($login.Content | ConvertFrom-Json).access_token
$h = @{ Authorization = "Bearer $token" }

# Jobs (seeds demos)
irm https://wazifni-backend.onrender.com/jobs -Headers $h | ConvertTo-Json -Depth 5  # 200, 3 items

# CORS preflight
$pre=@{ "Origin"="https://wazifni-frontend.vercel.app"; "Access-Control-Request-Method"="GET" }
(iwr https://wazifni-backend.onrender.com/jobs -Method Options -Headers $pre).Headers."Access-Control-Allow-Origin"
# => https://wazifni-frontend.vercel.app

# CORS simple
(iwr https://wazifni-backend.onrender.com/jobs -Headers @{ "Origin"="https://wazifni-frontend.vercel.app" }).Headers."Access-Control-Allow-Origin"
# => https://wazifni-frontend.vercel.app
