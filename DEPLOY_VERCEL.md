# Deploying to Vercel with Nile DB

This project is configured for easy deployment to Vercel.

## 1. Prerequisites
- A [Vercel](https://vercel.com/) account.
- A [Nile](https://www.thenile.dev/) database (create two databases or two schemas for dev/prod).
- The Vercel CLI installed (`npm i -g vercel`) OR connect your GitHub repository to Vercel.

## 2. Configuration for Nile DB
Nile provides a PostgreSQL connection string. You will need to extract the following components:
- **Host**: e.g., `db.thenile.dev`
- **Database Name**: e.g., `uiwiz`
- **User**: e.g., `user_...`
- **Password**: Your database password

## 3. Deployment Steps

### Method A: Using Vercel CLI (Recommended for first time)
1. Run `vercel` in the root directory.
2. Follow the prompts to link the project.
3. Set your Environment Variables in the Vercel Dashboard or via CLI:
   ```bash
   vercel env add DB_NAME production
   vercel env add DB_USER production
   vercel env add DB_PASSWORD production
   vercel env add DB_HOST production
   vercel env add DB_PORT production
   vercel env add GEMINI_API_KEY production
   ```
   Do the same for `development` if you want to use a separate Nile DB for local development/preview.

4. Deploy:
   ```bash
   vercel --prod
   ```

### Method B: Using GitHub Integration
1. Push your code to a GitHub repository.
2. Go to Vercel Dashboard -> "New Project".
3. Import your repository.
4. In "Environment Variables", add the following:
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`
   - `DJANGO_SECRET_KEY` (Generate a random string)
   - `DJANGO_DEBUG` (Set to `False` for production)
   - `GEMINI_API_KEY`
5. Click "Deploy".

## 4. Environment Switching (Dev vs Prod)
Vercel handles this automatically. You can add the same environment variable name (e.g., `DB_HOST`) multiple times in the Vercel Dashboard and assign each to different environments:
- **Production**: Point to your Nile Prod DB.
- **Preview/Development**: Point to your Nile Dev DB.

## 5. Notes on Nile DB
- The project is configured to use `sslmode=require` automatically in production (whenever `DEBUG=False`).
- Static files are served using `WhiteNoise`.

## 6. Database Migrations
Vercel serverless functions are not ideal for running migrations. To run migrations on your Nile DB:
1. Temporarily point your local `config.properties` to the Production Nile DB.
2. Run: `python backend/manage.py migrate`
3. Switch back to your Dev DB.

Alternatively, you can use a GitHub Action to run migrations on every push to the main branch.
