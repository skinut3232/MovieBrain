# MovieBrain — Product Requirements Document

## 1. Overview

MovieBrain is a full-stack movie tracking and recommendation application. Users log movies they've watched, rate them, and receive AI-powered personalized recommendations based on their taste profile. The app combines data from IMDb (292K movie catalog), TMDB (posters, trailers, streaming availability), OMDb (Rotten Tomatoes and Metacritic scores), and OpenAI (embeddings for similarity search and mood-based recommendations).

### Core Value Proposition

Most movie recommendation tools either rely on collaborative filtering ("people who liked X also liked Y") or simple genre matching. MovieBrain uses vector embeddings to build a mathematical representation of each user's taste, enabling nuanced recommendations that understand the relationship between movies at a deeper level — considering genre, director, cast, and era together rather than any single attribute.

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI (Python 3.12) | REST API, async-capable |
| **Database** | PostgreSQL 16 + pgvector | Relational data + vector similarity search |
| **ORM** | SQLAlchemy 2.0 | Database models and queries |
| **Migrations** | Alembic | Schema versioning (10 migrations to date) |
| **Frontend** | React 19 + TypeScript | UI framework |
| **Build** | Vite | Fast dev server and production bundling |
| **Styling** | Tailwind CSS 4 | Utility-first dark theme |
| **Charts** | Recharts | Stats dashboard visualizations |
| **Auth** | JWT (python-jose + bcrypt) | Stateless token authentication |
| **APIs** | OpenAI, TMDB, OMDb | Embeddings, metadata, critic scores |
| **Deployment** | Docker Compose + nginx | Containerized with SSL termination |

### Why These Choices

- **FastAPI over Django/Flask**: Native Pydantic validation, auto-generated OpenAPI docs, async support for external API calls. The app is API-first with a separate frontend, so Django's template system adds no value.
- **pgvector over Pinecone/Weaviate**: Keeps everything in one database. No need for a separate vector DB service when PostgreSQL can handle both relational queries and cosine similarity search at our scale (~292K movies).
- **SQLAlchemy raw SQL in discovery.py**: The browse/filter queries require dynamic WHERE clause construction with 10+ optional filters. Raw `text()` queries are more readable and performant than building complex ORM chains.
- **React + Vite over Next.js**: No SSR needed — the app is entirely client-rendered behind authentication. Vite provides fast HMR and simple configuration.
- **Tailwind over component libraries**: Full design control for the dark-themed UI without fighting component library defaults. The app has a consistent amber-on-dark-gray visual identity.

---

## 3. Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────┐
│  Browser (React SPA)                                │
│  - Auth context (JWT in localStorage)               │
│  - Profile context (multi-profile support)          │
│  - URL-driven filter state (Explore page)           │
└──────────────┬──────────────────────────────────────┘
               │ HTTP (axios)
               ▼
┌──────────────────────────────────────────┐
│  nginx (production only)                 │
│  - SSL termination (Let's Encrypt)       │
│  - /api/* → backend (prefix stripped)    │
│  - /* → static files + SPA fallback      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  FastAPI Backend                         │
│  - 9 routers, 50+ endpoints             │
│  - Rate limiting (slowapi)              │
│  - Security headers middleware           │
│  - JWT authentication                    │
├──────────────┬───────────────────────────┤
│  Services    │  External APIs            │
│  - auth      │  - TMDB (posters,         │
│  - catalog   │    trailers, providers,   │
│  - discovery │    trending)              │
│  - recommend │  - OMDb (RT, Metacritic)  │
│  - watch     │  - OpenAI (embeddings,    │
│  - stats     │    mood chat)             │
│  - tmdb      │                           │
│  - omdb      │                           │
│  - embedding │                           │
│  - collection│                           │
│  - list/flag │                           │
└──────────────┴───────────┬───────────────┘
                           │
                           ▼
┌──────────────────────────────────────────┐
│  PostgreSQL 16 + pgvector                │
│  - catalog_titles (292K movies)          │
│  - movie_embeddings (1536-dim vectors)   │
│  - profile_taste (per-user taste vector) │
│  - watches, tags, lists, flags           │
│  - trending_cache, watch_providers       │
│  - catalog_ratings (IMDb + RT + MC)      │
└──────────────────────────────────────────┘
```

### Key Architectural Patterns

**Lazy TMDB/OMDb Fetching**
External metadata (posters, overviews, trailers, streaming providers, RT scores) is fetched on-demand when a user first views a movie, then cached in the database. This avoids upfront bulk-fetching 292K movies from rate-limited APIs. The pattern is `get_or_fetch_*` — check DB first, call API if missing, save result, return.

**Vector-Based Recommendations**
Each movie has a 1536-dimensional embedding generated from its metadata text: `"{title} ({year}). {genres}. Directed by {directors}. Starring {cast}."` using OpenAI's text-embedding-3-small. A user's taste vector is the weighted average of their rated movie embeddings (rating value as weight, with a recency bonus). Recommendations are found via pgvector cosine similarity, blended 70/30 with a popularity score (RT Tomatometer or IMDb rating).

**Hybrid Mood Search**
Pure embedding search struggles with mood queries like "something scary" because embeddings encode metadata, not vibes. The solution is two-phase: (1) an LLM suggests ~20 specific movie titles matching the mood, which are looked up in the catalog; (2) embedding search finds less obvious picks. Results are merged — obvious choices first, discovery picks after.

**URL as State (Explore Page)**
All filter state lives in URL search params via the `useFilterParams` hook. This makes filtered views shareable, bookmarkable, and back-button friendly. The hook handles legacy param compatibility (`genre` → `genres`, `decade` → year range).

---

## 4. Data Model

### Core Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `catalog_titles` | ~292K | Movie metadata from IMDb + TMDB enrichment |
| `catalog_ratings` | ~292K | IMDb avg/votes + RT Tomatometer + Metacritic |
| `catalog_people` | ~590K | Actors, directors, writers from IMDb |
| `catalog_principals` | ~2.1M | Cast/crew role assignments |
| `catalog_crew` | ~292K | Director/writer arrays per movie |
| `catalog_akas` | ~736K | Alternative titles by region/language |
| `movie_embeddings` | ~292K | 1536-dim OpenAI vectors per movie |
| `trending_cache` | ~20 | Weekly TMDB trending, auto-refreshed |
| `watch_providers` | varies | Streaming availability (lazy-fetched per movie) |
| `provider_master` | ~100 | Streaming service metadata |

### User Tables

| Table | Purpose |
|-------|---------|
| `users` | Accounts (email + bcrypt password) |
| `profiles` | Multi-profile per user (each with independent history) |
| `watches` | Watch log entries with 1-10 ratings, notes, tags |
| `tags` / `watch_tags` | User-defined tags on watches |
| `movie_lists` / `list_items` | Custom lists (watchlist, favorites, rewatch, custom) |
| `movie_flags` | Not interested / don't recommend flags |
| `profile_taste` | Computed taste vector per profile |
| `onboarding_movies` / `skipped_onboarding_movies` | Onboarding flow state |
| `collections` / `collection_items` | Curated and auto-generated collections |

### Migration History

| # | Migration | What It Added |
|---|-----------|---------------|
| 1 | `b27df8dbee4b` | Initial schema — catalog, users, profiles, watches, tags, lists, flags |
| 2 | `f8650a768763` | Refined personal logging tables — timestamps, unique constraints |
| 3 | `c3a1e5f29d01` | Recommender tables — movie_embeddings, profile_taste (pgvector) |
| 4 | `f6c4d0e93b15` | TMDB integration — tmdb_id column, trending_cache table |
| 5 | `d4a2b7c91e03` | Poster + onboarding — poster_path, onboarding_movies table |
| 6 | `e5b3f9d82a04` | Discovery — collections, collection_items, indexes |
| 7 | `b8e6f2a13d37` | OMDb — rt_critic_score, rt_audience_score, metacritic_score on catalog_ratings |
| 8 | `a7d5e1f02c26` | Providers — overview/trailer on titles, watch_providers + provider_master tables |
| 9 | `c9d3e4f56a78` | Performance — missing indexes |
| 10 | `d1a2b3c4e5f6` | Language — original_language column on catalog_titles |

---

## 5. Features Built

### Authentication & Profiles
- Email/password registration and login with JWT tokens
- Multi-profile support (each user can have separate profiles with independent watch history and taste)
- Rate limiting on auth endpoints (5 registrations/min, 10 logins/min)

### Movie Catalog & Search
- Full-text search using PostgreSQL tsvector with filters (year range, genre, min rating)
- 292K movie catalog sourced from IMDb data dumps
- Rich detail pages with poster, overview, trailer (YouTube modal), cast, crew, alternate titles
- Critic scores: IMDb rating, RT Tomatometer (fresh/rotten icons), Metacritic (color-coded badge)
- Person pages with full filmography grouped by role
- Streaming provider availability per movie with clickable provider links

### Explore & Discovery
- Featured home view with trending, new releases, and genre-specific rows (horizontal scroll)
- Advanced browse with rich filter sidebar:
  - Multi-genre selection (OR logic) with chip UI
  - Year range, RT score minimum, runtime range
  - Language filter (original language from TMDB)
  - Streaming provider filter (logo chips)
  - Sort by popularity, rating, year
  - Hide watched toggle
- Surprise Me — random movie picker with genre filter
- Auto-generated collections (Top Rated 80s, Best Horror, etc.)
- Mobile responsive: sidebar becomes a drawer on small screens

### Watch Logging
- Rate movies 1-10, add notes, mark watched date
- Tag system (user-defined, applied per watch)
- Rewatch counter
- Custom lists: watchlist, favorites, rewatch, custom types
- Flag movies as "not interested" or "don't recommend"

### Recommendations
- Taste vector computed from rated movie embeddings (weighted by rating + recency bonus)
- Cosine similarity search via pgvector, blended with popularity score (70/30)
- Mood-based recommendations: describe what you're in the mood for
  - 8 preset mood chips (Feel-good, Mind-bending, Edge of my seat, etc.) — multi-selectable
  - Free-text mood input
  - Hybrid search: LLM title suggestions + embedding discovery
- Recommendation filters: genre, year range, runtime, min IMDb rating
- Fallback mode for users with < 5 ratings (popularity-based)
- Recency boost: recent ratings contribute more to taste vector

### Stats Dashboard
- Hero stats: total movies, average rating, hours watched, rewatches, unique languages
- Rating distribution (bar chart, 1-10)
- Genre breakdown (pie chart)
- Decade distribution (bar chart)
- Language diversity (pie chart)
- Top 10 directors and actors by watch count + avg rating
- You vs Critics scatter plot (user rating vs RT/IMDb)
- Movies per month (area chart)
- Rating trend over time (line chart)
- Highest and lowest rated movie lists
- Recent watches section
- Expandable full watch history

### Onboarding
- Quick-rate flow for new users to build initial taste profile
- Curated movie selection, load more batches
- Skip option for unseen movies
- Progress indicator showing rated count vs minimum required (5)

### Production Readiness (latest)
- Configurable CORS origins (env var, defaults to localhost for dev)
- Database connection pooling (pool_size, max_overflow, pool_pre_ping)
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Health check endpoint with database probe (returns 503 if DB unreachable)
- Frontend API URL via environment variable (`VITE_API_URL`)
- Error boundaries and toast notifications
- Docker Compose setup (backend, PostgreSQL+pgvector, nginx)
- nginx config with SSL, HTTPS redirect, SPA fallback, gzip, asset caching
- Production override file (closed ports, certbot auto-renewal)
- Deployment script for VPS setup

---

## 6. Project Structure

```
MovieBrain/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, middleware, health check
│   │   ├── config.py               # Pydantic settings from .env
│   │   ├── database.py             # SQLAlchemy engine + session factory
│   │   ├── core/
│   │   │   └── dependencies.py     # get_db, get_current_user, get_verified_profile
│   │   ├── routers/
│   │   │   ├── auth.py             # Register, login (rate limited)
│   │   │   ├── catalog.py          # Search, browse, details, genres, languages, providers
│   │   │   ├── profiles.py         # CRUD profiles
│   │   │   ├── watches.py          # Watch logging, history, stats, tags
│   │   │   ├── recommend.py        # Recommendations + taste profile
│   │   │   ├── onboarding.py       # Quick-rate onboarding flow
│   │   │   ├── collections.py      # Curated/auto collections
│   │   │   ├── lists.py            # Custom lists (watchlist, favorites, etc.)
│   │   │   └── flags.py            # Not interested / don't recommend
│   │   ├── services/
│   │   │   ├── auth.py             # JWT + bcrypt
│   │   │   ├── catalog.py          # Full-text search, title detail
│   │   │   ├── discovery.py        # Browse queries (raw SQL), featured rows, similar
│   │   │   ├── tmdb.py             # TMDB API (lazy-fetch poster/overview/trailer/providers)
│   │   │   ├── omdb.py             # OMDb API (lazy-fetch RT/Metacritic, 90-day cache)
│   │   │   ├── recommender.py      # Taste vectors, mood search, hybrid recommendations
│   │   │   ├── embedding.py        # Embedding text builder
│   │   │   ├── watch.py            # Watch CRUD, tag resolution
│   │   │   ├── stats.py            # 11 aggregate SQL queries for stats dashboard
│   │   │   ├── collection.py       # Collection queries + default seeding
│   │   │   ├── list.py             # List CRUD + reordering
│   │   │   └── flag.py             # Flag CRUD
│   │   ├── models/
│   │   │   ├── catalog.py          # CatalogTitle, CatalogRating, CatalogPerson, etc.
│   │   │   ├── user.py             # User, Profile, OnboardingMovie
│   │   │   ├── personal.py         # Watch, Tag, MovieList, ListItem, MovieFlag
│   │   │   ├── recommender.py      # MovieEmbedding, ProfileTaste (pgvector)
│   │   │   └── collection.py       # Collection, CollectionItem
│   │   └── schemas/                # Pydantic request/response models (35+ schemas)
│   ├── alembic/                    # 10 migrations
│   ├── scripts/                    # Data seeding (IMDb ingest, embeddings, posters, etc.)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx                # Entry point (providers, Sonner toasts)
│   │   ├── App.tsx                 # Routes (15 routes, ProtectedRoute wrapper)
│   │   ├── api/                    # Axios client + API functions (8 files)
│   │   ├── pages/                  # 12 page components
│   │   ├── components/
│   │   │   ├── layout/             # AppLayout, Navbar
│   │   │   ├── auth/               # LoginForm, RegisterForm
│   │   │   ├── common/             # MoviePoster, MovieGrid
│   │   │   ├── movie/              # MovieDetail, CriticScores, MovieActions, etc.
│   │   │   ├── catalog/            # SearchBar, SearchResults, TitleCard
│   │   │   ├── explore/            # FilterSidebar, GenreChips, MovieRow, SurpriseMe
│   │   │   ├── recommend/          # MoodInput, RecommendCard, RecommendFilters
│   │   │   ├── watches/            # WatchCard, WatchHistory
│   │   │   ├── onboarding/         # OnboardingCard
│   │   │   ├── lists/              # ListsPage, ListDetail, ListItem
│   │   │   └── stats/              # 11 chart/stat components + chartTheme
│   │   ├── context/                # AuthContext, ProfileContext
│   │   ├── hooks/                  # useDebounce, useFilterParams
│   │   ├── types/                  # TypeScript interfaces (index.ts)
│   │   └── utils/                  # languageCodes.ts
│   └── index.html
├── nginx/
│   └── nginx.conf                  # Reverse proxy, SSL, SPA fallback
├── docker-compose.yml              # Dev: db + backend + web
├── docker-compose.prod.yml         # Prod overrides: closed ports, certbot
├── Dockerfile.web                  # Multi-stage: Node build → nginx
├── deploy.sh                       # VPS deployment script
└── CLAUDE.md                       # AI context file
```

---

## 7. API Endpoint Summary

### Auth (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account (5/min rate limit) |
| POST | `/auth/login` | Login, returns JWT (10/min rate limit) |

### Profiles (`/profiles`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/profiles` | List user's profiles |
| POST | `/profiles` | Create profile |
| PATCH | `/profiles/{id}` | Update profile name |
| DELETE | `/profiles/{id}` | Delete profile (cascades) |

### Catalog (`/catalog`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/catalog/search` | Full-text search with filters |
| GET | `/catalog/browse` | Advanced filtered browse (10+ filter params) |
| GET | `/catalog/random` | Random movie with optional filters |
| GET | `/catalog/titles/{id}` | Full movie detail (lazy-fetches TMDB + OMDb) |
| GET | `/catalog/titles/{id}/similar` | Embedding-based similar movies |
| GET | `/catalog/titles/{id}/providers` | Streaming availability |
| GET | `/catalog/people/{id}` | Person detail + filmography |
| GET | `/catalog/featured-rows` | Curated discover rows |
| GET | `/catalog/featured-genres` | Featured genre list |
| GET | `/catalog/genres` | All genres |
| GET | `/catalog/decades` | All decades |
| GET | `/catalog/languages` | Languages with counts |
| GET | `/catalog/providers` | Streaming providers with counts |
| POST | `/catalog/trending/refresh` | Refresh TMDB trending cache |
| POST | `/catalog/providers/refresh` | Refresh provider master list |

### Watches (`/profiles/{id}`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/profiles/{id}/watches` | Log/update watch with rating |
| GET | `/profiles/{id}/history` | Paginated watch history |
| GET | `/profiles/{id}/stats` | Full stats dashboard data |
| DELETE | `/profiles/{id}/watches/{titleId}` | Remove watch |
| GET | `/profiles/{id}/tags` | List tags |
| POST | `/profiles/{id}/tags` | Create tag |
| DELETE | `/profiles/{id}/tags/{tagId}` | Delete tag |

### Recommendations (`/profiles/{id}`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/profiles/{id}/recommend` | Get recommendations (optional mood) |
| GET | `/profiles/{id}/taste` | Taste profile status |
| POST | `/profiles/{id}/taste/recompute` | Force taste recomputation |

### Lists (`/profiles/{id}/lists`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/profiles/{id}/lists` | List user's lists |
| POST | `/profiles/{id}/lists` | Create list |
| GET | `/profiles/{id}/lists/{listId}` | List detail with items |
| PATCH | `/profiles/{id}/lists/{listId}` | Update list name |
| DELETE | `/profiles/{id}/lists/{listId}` | Delete list |
| POST | `/profiles/{id}/lists/{listId}/items` | Add item |
| PATCH | `/profiles/{id}/lists/{listId}/items/reorder` | Reorder items |
| DELETE | `/profiles/{id}/lists/{listId}/items/{titleId}` | Remove item |

### Collections, Flags, Onboarding
| Method | Path | Description |
|--------|------|-------------|
| GET | `/collections` | All collections |
| GET | `/collections/{id}` | Collection with movies |
| POST | `/profiles/{id}/flags` | Flag movie |
| GET | `/profiles/{id}/flags` | List flags |
| DELETE | `/profiles/{id}/flags/{titleId}` | Remove flag |
| GET | `/profiles/{id}/onboarding-movies` | Get onboarding batch |
| POST | `/profiles/{id}/onboarding-skip` | Skip onboarding movie |
| POST | `/profiles/{id}/onboarding-complete` | Finish onboarding |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (DB probe, returns 503 if down) |

---

## 8. Recommendation Algorithm

### Taste Vector Construction
1. Fetch all rated movies for the profile with their embeddings
2. Weight each embedding by `rating_value + recency_bonus`
   - Recency bonus: up to 0.2 extra weight for ratings within last 90 days (linear ramp)
3. Compute weighted average of all embeddings
4. L2-normalize the result → taste vector (1536 dims)
5. Cache in `profile_taste` table

### Standard Recommendations
1. Retrieve taste vector from cache (recompute if stale)
2. pgvector cosine similarity search against `movie_embeddings`
3. Exclude already-watched and flagged movies
4. Apply optional filters (genre, year, runtime, rating)
5. Compute blended score: `0.70 * cosine_similarity + 0.30 * popularity`
   - Popularity = `COALESCE(rt_critic_score/100, average_rating/10, 0.5)`
6. Sort by blended score descending
7. Return paginated results

### Mood-Based Recommendations
1. User provides mood text (presets + custom)
2. **Phase 1 — LLM Title Suggestions**: GPT-4o-mini suggests ~20 specific movie titles matching the mood, considering the user's top-rated movies for taste context. These are looked up in the catalog.
3. **Phase 2 — Embedding Discovery**: LLM generates an ideal movie description from the mood. This is embedded and blended with the taste vector (60% mood, 40% taste). pgvector search finds matches.
4. **Merge**: LLM picks first (obvious choices), then embedding picks (discovery), deduplicated.

### Fallback Mode
Users with < 5 ratings get popularity-sorted results instead of vector recommendations.

---

## 9. Data Pipeline

### Initial Setup
1. **`ingest_imdb.py`** — Downloads IMDb TSV dumps, parses ~292K movies (type=movie only), bulk-inserts titles, ratings, people, principals, crew, akas
2. **`generate_embeddings.py`** — Batch-processes movies with ratings, builds metadata text, calls OpenAI text-embedding-3-small, stores 1536-dim vectors
3. **`seed_onboarding.py`** — Populates curated onboarding movie set

### Enrichment (bulk seeding scripts)
4. **`seed_tmdb_posters.py`** — Backfills poster paths from TMDB
5. **`seed_omdb_ratings.py`** — Bulk-fetches RT Tomatometer + Metacritic for top N popular movies
6. **`seed_original_language.py`** — Backfills original_language from TMDB API
7. **`seed_providers.py`** — Fetches streaming availability data

### Runtime Enrichment
- Movie detail view triggers lazy-fetch of poster, overview, trailer, original_language (TMDB) and RT/Metacritic scores (OMDb, 90-day cache)
- Streaming providers lazy-fetched per movie on first view
- TMDB trending cache refreshable via API endpoint

---

## 10. What Still Needs to Be Done

### Deployment (Ready to Execute)
- [ ] Provision a VPS (DigitalOcean, Hetzner, etc.)
- [ ] Register and configure a domain name
- [ ] Run `deploy.sh` on the VPS
- [ ] Transfer local database via `pg_dump` → SCP → `pg_restore`
- [ ] Verify SSL, health check, and full user flow

### Security & Auth Hardening
- [ ] **Email verification** — Confirm email on registration before granting full access
- [ ] **Password reset flow** — Forgot password email with reset token
- [ ] **httpOnly cookies** — Migrate JWT from localStorage to httpOnly cookies (prevents XSS token theft)
- [ ] **CSRF protection** — Required once using cookies for auth
- [ ] **Account lockout** — Temporarily lock accounts after repeated failed login attempts

### Observability & Reliability
- [ ] **Structured logging** — JSON-formatted logs with request IDs for debugging
- [ ] **Error tracking** — Sentry integration for automatic error reporting
- [ ] **Application metrics** — Request latency, error rates, DB query timing
- [ ] **Database backups** — Automated daily pg_dump to object storage
- [ ] **Alerting** — Notify on health check failures or error rate spikes

### CI/CD
- [ ] **Automated tests** — Unit tests for services, integration tests for endpoints (pytest fixtures exist but no tests written yet)
- [ ] **CI pipeline** — GitHub Actions: lint, type-check, test on every PR
- [ ] **CD pipeline** — Auto-deploy to VPS on merge to main

### Feature Ideas
- [ ] **Social features** — Follow friends, see what they're watching, shared lists
- [ ] **Reviews** — Longer-form text reviews (beyond the current notes field)
- [ ] **TV show support** — The IMDb data includes TV series; extend catalog to support them
- [ ] **Watchlist recommendations** — "From your watchlist, watch this next" based on mood or taste
- [ ] **Notification system** — "A movie on your watchlist is now streaming on Netflix"
- [ ] **Import from Letterboxd/IMDb** — CSV import of existing watch history
- [ ] **Advanced taste analytics** — "Your taste is 73% similar to Roger Ebert" style comparisons
- [ ] **Movie club / group watch** — Shared lists with voting on what to watch next
- [ ] **Seasonal/themed collections** — Auto-generated "Halloween picks" or "Summer blockbusters" based on date
- [ ] **Recommendation explanations** — "Recommended because you loved Inception and The Matrix"

### Performance & Scale
- [ ] **Redis caching** — Cache frequent queries (featured rows, genre lists, trending) to reduce DB load
- [ ] **CDN for posters** — Proxy TMDB images through a CDN instead of direct-linking
- [ ] **Embedding refresh** — Re-generate embeddings when movie metadata is enriched (e.g., after adding RT scores to embedding text)
- [ ] **Background tasks** — Celery or similar for async TMDB/OMDb fetching instead of blocking on user requests
- [ ] **Database read replicas** — If the app scales beyond what a single Postgres instance handles

---

## 11. Configuration Reference

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/moviebrain` | PostgreSQL connection string |
| `SECRET_KEY` | (must change in prod) | JWT signing key |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `CORS_ORIGINS` | `""` (empty = localhost regex) | Comma-separated allowed origins |
| `ROOT_PATH` | `""` | Set to `/api` in production (for Swagger docs behind proxy) |
| `DB_POOL_SIZE` | `5` | SQLAlchemy connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Max connections above pool size |
| `OPENAI_API_KEY` | | OpenAI API key (embeddings + mood chat) |
| `TMDB_API_KEY` | | TMDB API key (posters, trailers, trending, providers) |
| `OMDB_API_KEY` | | OMDb API key (RT Tomatometer, Metacritic) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMENSIONS` | `1536` | Embedding vector size |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Model for mood description generation |
| `MOOD_BLEND_WEIGHT` | `0.6` | Mood vs taste vector blend (0.6 = 60% mood) |
| `RECENCY_BOOST` | `0.2` | Max extra weight for recent ratings |
| `RECENCY_WINDOW_DAYS` | `90` | Window for recency bonus |
| `POPULARITY_WEIGHT` | `0.30` | Popularity vs similarity blend (0.30 = 30% popularity) |
| `RECOMMEND_DEFAULT_LIMIT` | `20` | Default recommendation page size |
| `RECOMMEND_MIN_RATED_MOVIES` | `5` | Minimum ratings before vector recs activate |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL (set to `/api` in production) |

---

## 12. Development History

| Commit | Milestone |
|--------|-----------|
| `926982d` | **Milestone 1**: Backend API with IMDb catalog (292K movies ingested) |
| `9374856` | **Milestone 2**: Personal logging + React frontend (watches, ratings, tags) |
| `cc82503` | **Milestone 3**: Recommender core (embeddings, vector similarity, taste profiles) |
| `ae070cc` | **Milestone 4**: Onboarding + TMDB poster integration |
| `b13f463` | README with setup docs |
| `7e60573` | **Milestone 5**: Discovery, browsing, rich metadata (detail pages, trailers) |
| `81bc57d` | TMDB trending integration (weekly auto-refresh) |
| `c5c98e1` → `c23f7d1` | Rich filter sidebar, streaming providers, OMDb/RT scores |
| `ad5cdc3` → `13a5c41` | Mood-based recommendations, hybrid search, multi-select presets |
| `e6e57ee` | Original language from TMDB (fixed language filter) |
| `f707911` → `5a1a424` | UI polish (trailer modal, provider links, RT scores everywhere) |
| `aad021a` | Stats dashboard (11 visualizations replacing flat watch history) |
| `cd6c1d4` | Production readiness (Docker, nginx, rate limiting, security headers) |
