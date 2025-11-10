# Wazifni Full CI/CD, QA & Troubleshooting Workflow

This document outlines the end‑to‑end steps for maintaining a healthy continuous integration and deployment pipeline for the **Wazifni** project, along with quality assurance (QA) validation and troubleshooting guidance.

## Stage 1 – Verify Build

1. Trigger the workflow via GitHub Actions or the CLI:

   ```bash
   gh run watch
   ```

   or navigate to **GitHub → Actions** and select **Frontend CI + Deploy**.

2. Run the `verify` job, which executes linting, type‑checks, tests, and the build:

   ```bash
   npm run lint && npm run verify
   ```

3. Expect output similar to:

   ```
   ✅ Lint passed
   ✅ Type‑check passed
   ✅ Tests passed
   ✅ Build successful
   ```

4. Ensure the workflow log shows the build completed and is ready to deploy:

   ```
   Build & Verify completed
   Proceeding to Deploy to Vercel (Preview)
   ```

## Stage 2 – Deploy to Vercel (Staging)

1. The GitHub Action automatically runs:

   ```bash
   npx vercel --token=${{ secrets.VERCEL_TOKEN }}
   ```

2. Confirm success in the logs. A typical deploy will output lines like:

   ```
   ✅ Deployment complete: https://wazifni‑frontend‑git‑main‑adamsalemsmu‑svg.vercel.app
   ✅ Alias updated: wazifni‑frontend‑staging.vercel.app
   ```

3. If you need to redeploy manually:

   ```bash
   cd frontend
   npx vercel --prod --token=$VERCEL_TOKEN
   ```

## Stage 3 – QA Smoke Verification

After a successful deploy, run the smoke test script:

```bash
bash scripts/qa_smoke.sh
```

Expect output like:

```
✅ Dashboard reachable
✅ Footer year displayed correctly
✅ /jobs/run API reachable
✅ Backend health OK
✨ All smoke tests complete!
```

## Stage 4 – Staging QA Manual Checks

Open the staging environment:

```
https://wazifni‑frontend‑staging.vercel.app/en/dashboard
```

Verify the following:

| Component         | Expected Behavior                                           |
| ----------------- | ----------------------------------------------------------- |
| **Analytics**     | Displays totals, success/failure counts, and average time. |
| **Notifications** | Bell icon shows in‑app messages and toasts correctly.       |
| **Automation**    | `/jobs/run` endpoint returns a 200 HTTP response.           |
| **Assistant**     | Assistant panel opens and responds without errors.          |
| **Footer**        | Legal text shows the current year.                          |

## Stage 5 – Backend Verification

Use cURL or your preferred tool to hit the backend automation endpoint:

```bash
curl -i https://api.wazifni.ai/jobs/run
```

The response should include:

```
HTTP/1.1 200 OK
```

Also confirm your backend migrations and task workers are healthy:

```bash
gh run list --workflow "Backend CI / Alembic"
```

## Stage 6 – Production Release

After staging passes QA:

```bash
git tag -a v1.0.0‑beta3 -m "Wazifni Beta 3 – Automation + Notifications verified"
git push origin v1.0.0‑beta3
```

Tagging a release triggers the production deploy and updates the live site at:

```
https://wazifni.ai
```

## Troubleshooting – `DEPLOYMENT_NOT_FOUND` on Vercel

If your staging URL returns a 404 or shows `DEPLOYMENT_NOT_FOUND`, follow these steps:

### 1. Check CI Logs

```bash
gh run list --workflow "Frontend CI + Deploy" --limit 3
gh run view <run-id> --log
```

Look for messages such as:

```
Error! Could not retrieve deployment or project not linked
```

### 2. Find the Valid Deployment URL

Check the deploy step in the GitHub Action log or visit the Vercel dashboard’s **Deployments** tab. Copy the most recent unique URL, for example:

```
https://wazifni‑frontend‑git‑main‑adamsalemsmu‑svg.vercel.app
```

### 3. Re‑link the Staging Alias

If the stable subdomain does not exist or has expired, run:

```bash
npx vercel alias add \
  https://wazifni‑frontend‑git‑main‑adamsalemsmu‑svg.vercel.app \
  wazifni‑frontend‑staging.vercel.app \
  --token $VERCEL_TOKEN
```

### 4. Redeploy (if Needed)

If the deployment failed entirely, redeploy:

```bash
cd frontend
npx vercel --prod --token=$VERCEL_TOKEN
```

### 5. Validate

Visit your staging URL again, e.g.:

```
https://wazifni‑frontend‑staging.vercel.app/en/dashboard
```

Verify that the dashboard loads, notifications show, automation triggers are available, and the footer year is correct.

When you see a 200 OK and all features working, your deployment is restored.

## Stage 7 – Continuous QA & Reporting

To show the status of your pipeline in your README, include a badge like:

```markdown
![Smoke Tests](https://github.com/adamsalemsmu-svg/wazfini-jobright-suite/actions/workflows/frontend-ci.yml/badge.svg)
```

You can schedule regular verification runs with:

```bash
gh workflow run "Frontend CI + Deploy"
```gh workflow run "Frontend CI + Deploy"
```
