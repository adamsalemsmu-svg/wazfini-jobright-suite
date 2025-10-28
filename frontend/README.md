# Wazifni Frontend MVP

A bilingual (English + Arabic) frontend for the Wazifni platform built with:

- Next.js App Router (`src/app`)
- Tailwind CSS + shadcn/ui design tokens
- `next-intl` locale routing with middleware
- React Query for data fetching
- Zustand for lightweight auth state

## Environment

Copy the example file to configure local env vars:

```bash
cp .env.local.example .env.local
```

Key variables:

- `NEXT_PUBLIC_API_URL`: FastAPI backend URL (defaults to Render deployment)
- `NEXT_PUBLIC_DEFAULT_LOCALE`: default language (`en`)
- `NEXT_PUBLIC_SUPPORTED_LOCALES`: comma-separated list (`en,ar`)
- `NEXT_PUBLIC_APP_NAME`: human-friendly label used across the UI (`Wazifni`)

## Development

```bash
npm install
npm run dev
```

Open `http://localhost:3000` to view the app. Locale-prefixed routes (e.g. `/en/login`, `/ar/dashboard`) are handled via `middleware.ts`.

Useful scripts:

```bash
npm run lint   # static analysis
npm run build  # production build check
```

## Project Highlights

- Auth flows (`/src/app/[locale]/(auth)/*`) integrate with backend endpoints for login, registration, and password reset.
- Dashboard shell provides a sidebar/topbar layout with locale toggle and placeholder content.
- `src/messages/*.json` stores translations; add new keys in both locales.
- `components.json` keeps shadcn/ui configuration aligned with Tailwind tokens.

## Deployment Guide

### Prepare the project

1. Commit and push all changes to GitHub.
2. Ensure `npm run lint` and `npm run build` pass locally.

### Configure Vercel

1. Open the [Vercel dashboard](https://vercel.com/dashboard) and import this repository.
2. Use the **Next.js** framework preset. Build command: `npm run build`. Output directory: `.next`.
3. Add the following Environment Variables under the **Production** environment:
	- `NEXT_PUBLIC_API_URL=https://wazifni-backend.onrender.com`
	- `NEXT_PUBLIC_DEFAULT_LOCALE=en`
	- `NEXT_PUBLIC_SUPPORTED_LOCALES=en,ar`
	- `NEXT_PUBLIC_APP_NAME=Wazifni`
4. Trigger the deployment. Vercel will automatically detect the App Router and produce an optimized build.

### Post-deploy checks

1. Confirm the deployment URL responds with HTTP 200: `curl -I https://<deployment>.vercel.app`.
2. Repeat for the health check route if exposed (e.g. `/api/healthz`).
3. Visit `/en/login`, `/ar/login`, and `/en/dashboard` to verify locale routing, authentication, and RTL support.
4. Switch between light/dark themes, toggle locales, and ensure logout clears the session.

The frontend expects the FastAPI backend to manage authentication via HTTP-only cookies and CORS settings compatible with the Vercel domain.
