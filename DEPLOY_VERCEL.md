# Deploy UIWiz Backend on Vercel (Free Tier)

This guide walks you through deploying this Django backend on Vercel using the **free tier**.

## Prerequisites

- A [Vercel account](https://vercel.com/signup) (free)
- A [GitHub](https://github.com) (or GitLab/Bitbucket) account
- This repo pushed to a GitHub repository

---

## 1. Database (Free Tier)

Vercel does not provide a database. Use a **free Postgres** provider and set the connection via environment variables.

### Option A: Neon (recommended, free tier)

1. Go to [Neon](https://neon.tech) and sign up.
2. Create a new project and copy the **connection string** (e.g. `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`).

### Option B: Supabase

1. Go to [Supabase](https://supabase.com) and create a project.
2. In **Settings → Database**, copy the **Connection string (URI)**.

### Option C: Railway / ElephantSQL

- [Railway](https://railway.app) and [ElephantSQL](https://www.elephantsql.com) also offer free Postgres; use their connection URI.

---

## 2. Push Code to GitHub

If the project is not in a repo yet:

```bash
cd /path/to/uiwiz-backend
git init
git add .
git commit -m "Add Vercel deployment config"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## 3. Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New… → Project**.
3. **Import** your GitHub repository (`uiwiz-backend` or the repo name).
4. **Root Directory**: leave as **.** (project root).
5. **Framework Preset**: leave as **Other** (no framework).
6. Do **not** change Build Command or Output Directory; Vercel will use `vercel.json` and `api/wsgi.py`.

---

## 4. Set Environment Variables (Free Tier)

In the Vercel project: **Settings → Environment Variables**. Add these for **Production** (and optionally Preview):

| Variable | Description | Example / Notes |
|----------|-------------|------------------|
| `DJANGO_SECRET_KEY` | Django secret (required in prod) | Long random string (e.g. from `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DEBUG` | Set to `False` in production | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `.vercel.app,your-domain.com` (optional if you only use *.vercel.app) |
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | From your Neon/Supabase URI |
| `DB_USER` | Database user | From URI |
| `DB_PASSWORD` | Database password | From URI |
| `DB_HOST` | Database host | e.g. `ep-xxx.region.aws.neon.tech` (Neon) or Supabase host |
| `DB_PORT` | Database port | `5432` |
| `DB_SSLMODE` | SSL mode | `require` (recommended for Neon/Supabase) |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins | `https://your-frontend.vercel.app,https://your-domain.com` |
| `GEMINI_API_KEY` | (Optional) Default Gemini API key | From Google AI Studio |
| `GEMINI_MODEL` | (Optional) Gemini model | `gemini-2.0-flash` |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | (Optional) Path to Firebase JSON | Leave empty or use base64/env if you configure it later |

**Neon example (split from URI):**

- `DB_HOST` = host from URI (e.g. `ep-xxx.us-east-2.aws.neon.tech`)
- `DB_NAME` = database name (e.g. `neondb`)
- `DB_USER` = username from URI
- `DB_PASSWORD` = password from URI
- `DB_PORT` = `5432`
- `DB_SSLMODE` = `require`

---

## 5. Deploy

1. Click **Deploy** (or push to `main` if you already connected the repo).
2. Wait for the build to finish. The first run may take a few minutes (installing Python deps).
3. Your API will be at: **`https://<your-project>.vercel.app`**

Test:

- **`https://<your-project>.vercel.app/`** — root message
- **`https://<your-project>.vercel.app/api/health/`** — health check

---

## 6. Run Migrations (Required for DB)

Vercel’s build does **not** run Django migrations (no DB at build time). Run them once after the first deploy:

**Option A – From your machine (recommended)**

```bash
cd backend
# Set the same env vars as on Vercel (or use a .env file)
export DB_HOST=your-db-host
export DB_NAME=your-db-name
export DB_USER=your-user
export DB_PASSWORD=your-password
export DB_PORT=5432
export DB_SSLMODE=require
python manage.py migrate
```

**Option B – Vercel CLI**

1. Install [Vercel CLI](https://vercel.com/docs/cli): `npm i -g vercel`
2. Link: `vercel link`
3. Pull env: `vercel env pull .env.local`
4. In `backend/`, run: `python manage.py migrate` (after setting or sourcing env from `.env.local`)

---

## 7. Free Tier Limits (Vercel)

- **Serverless execution**: Free tier has limits on invocations and duration; sufficient for low–medium traffic.
- **Bandwidth**: Free tier includes a limited amount; enough for development and small projects.
- **Builds**: Free tier has a monthly build limit; usually enough for personal/small team use.

For more: [Vercel pricing](https://vercel.com/pricing).

---

## 8. Optional: Custom Domain

1. In Vercel: **Project → Settings → Domains**.
2. Add your domain and follow DNS instructions.
3. Add that domain to `DJANGO_ALLOWED_HOSTS` (e.g. `your-api.example.com`).

---

## Troubleshooting

- **502 / timeout**: Check Vercel function logs (Project → Deployments → select deployment → Functions). Increase timeout in **Settings → Functions** if needed (paid feature for longer timeouts).
- **Database errors**: Ensure all `DB_*` env vars match your Neon/Supabase (or other) connection string and that migrations have been run.
- **CORS errors**: Add your frontend URL to `CORS_ALLOWED_ORIGINS` (no trailing slash).
- **Static files**: This setup uses WhiteNoise; for heavy static usage, consider a CDN or separate static hosting.

---

## Summary Checklist

- [ ] Repo pushed to GitHub
- [ ] Free Postgres created (Neon/Supabase) and connection details noted
- [ ] Vercel project created and repo connected
- [ ] All required env vars set (especially `DJANGO_SECRET_KEY`, `DEBUG=False`, `DB_*`, `CORS_ALLOWED_ORIGINS`)
- [ ] First deploy completed
- [ ] Migrations run against the production DB
- [ ] Root and `/api/health/` tested on `https://<project>.vercel.app`
