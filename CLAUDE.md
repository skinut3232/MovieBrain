# MovieBrain - Claude Context

AI-powered movie tracking and recommendation app.

## Quick Start

```bash
# Backend (terminal 1)
cd backend
venv/Scripts/activate  # Windows
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend (terminal 2)
cd frontend
npm run dev
```

Backend: http://127.0.0.1:8000
Frontend: http://localhost:5173

## Tech Stack

- **Backend**: FastAPI, PostgreSQL + pgvector, SQLAlchemy, Alembic
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **APIs**: OpenAI (embeddings), TMDB (posters/trending)

## Project Structure

```
backend/
  app/
    routers/      # API endpoints (auth, catalog, profiles, watches, etc.)
    services/     # Business logic (tmdb.py, discovery.py, recommend.py)
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas
  alembic/        # Database migrations
  scripts/        # Data seeding scripts

frontend/
  src/
    pages/        # Route components
    components/   # Reusable UI components
    api/          # API client functions
    types/        # TypeScript interfaces
```

## Key Patterns

- **Lazy TMDB fetching**: Poster, overview, trailer fetched on-demand and cached in DB
- **Embeddings**: Movies have OpenAI embeddings stored in pgvector for similarity search
- **Profiles**: Multi-profile per user, each with own watch history and taste profile

## Database

Run migrations: `python -m alembic upgrade head`
Create migration: `python -m alembic revision -m "description"`

Key tables:
- `catalog_titles` - Movie catalog with IMDB data + TMDB metadata
- `watches` - User watch history with ratings
- `movie_embeddings` - Vector embeddings for recommendations
- `trending_cache` - Weekly TMDB trending cache

## Common Tasks

**Add new API endpoint:**
1. Add route in `backend/app/routers/`
2. Add service logic in `backend/app/services/`
3. Add schemas in `backend/app/schemas/`

**Add database column:**
1. Create migration in `backend/alembic/versions/`
2. Update model in `backend/app/models/`
3. Run `python -m alembic upgrade head`

## Obsidian Project Note

`C:\Users\Rob\Documents\Software\Obsidian\My Notebook\1 Projects\MovieBrain.md`

## Current State (Feb 2026)

Recent work:
- TMDB trending integration (weekly auto-refresh)
- Discovery page with featured rows
- Rich movie details (trailers, overviews)
- Onboarding flow with quick-rate

The app has ~292K movies from IMDB with embeddings generated.
