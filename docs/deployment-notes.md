# Deployment Notes

- Redeploy triggered on 2025-10-25 to refresh frontend deployment.
- Backend auto-deploy tested on 2025-10-25 after adding Render secrets.
- Re-verified Render secrets and re-triggered deploy on 2025-10-25.
- Added Render deploy hook secret on 2025-10-25 for CI auto-redeploy.

## Redeploy Steps (2025-10-28)

- Render post-deploy now runs `PYTHONPATH=. alembic upgrade head && python scripts/seed.py`, keeping the database migrated and seeded automatically.
- Trigger a new Render deploy for the backend service after landing schema changes.
- Monitor Render deploy logs until health checks pass and the API responds on `/health`.
