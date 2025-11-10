#!/usr/bin/env bash
#
# Wazifni QA Smoke Test
# Checks critical frontend and backend routes after deploy.

set -euo pipefail

# -------- CONFIG --------
FRONTEND_URL=${FRONTEND_URL:-"https://wazifni-frontend-staging.vercel.app"}
BACKEND_URL=${BACKEND_URL:-"https://wazifni-backend.onrender.com"}
DASHBOARD_PATH="/en/dashboard"
JOBS_API_PATH="/jobs/run"

echo "🔍 Running Wazifni Smoke Tests..."
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"

# -------- FRONTEND CHECKS --------
echo "🤑 Checking dashboard load..."
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$DASHBOARD_PATH" | grep -q "200"; then
  echo "✅ Dashboard reachable"
else
  echo "❌ Dashboard not reachable" && exit 1
fi

echo "📊 Checking for footer year..."
if curl -s "$FRONTEND_URL" | grep -q "$(date +%Y)"; then
  echo "✅ Footer year displayed correctly"
else
  echo "⚠️ Footer year missing"
fi

# -------- BACKEND CHECKS --------
echo "🤖 Checking automation endpoint..."
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$JOBS_API_PATH" | grep -q "200"; then
  echo "✅ /jobs/run API reachable"
else
  echo "❌ /jobs/run API unavailable" && exit 1
fi

echo "📬 Checking notification/health endpoints..."
if curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/healthz" | grep -q "200"; then
  echo "✅ Backend health OK"
else
  echo "⚠️ Health endpoint failed"
fi

echo "✨ All smoke tests complete!"
