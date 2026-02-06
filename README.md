# MovieBrain

AI-powered movie tracking and recommendation app with personalized suggestions based on your taste.

## Features

- **Movie Search** - Full-text search across 290K+ movies from IMDb catalog
- **Watch Tracking** - Log movies you've seen with ratings, notes, and tags
- **Custom Lists** - Create watchlists, favorites, and custom collections
- **AI Recommendations** - Personalized suggestions using OpenAI embeddings and vector similarity
- **Onboarding Flow** - Quick-rate popular movies to bootstrap your taste profile
- **TMDb Posters** - Movie poster images throughout the app

## Tech Stack

### Backend
- **FastAPI** - Python async web framework
- **PostgreSQL** - Database with pgvector extension for embeddings
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **OpenAI API** - Text embeddings for recommendations
- **TMDb API** - Movie poster images

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector extension

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL, OpenAI API key, and TMDb API key

# Run migrations
python -m alembic upgrade head

# Seed onboarding movies
python -m scripts.seed_onboarding

# Fetch movie posters (optional, takes ~10 min)
python -m scripts.fetch_posters --limit 10000

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at http://localhost:3000

## API Endpoints

### Auth
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login

### Profiles
- `GET /profiles` - List profiles
- `POST /profiles` - Create profile

### Catalog
- `GET /catalog/search?q=` - Search movies
- `GET /catalog/titles/{id}` - Movie details

### Watches
- `POST /profiles/{id}/watches` - Log a watch
- `GET /profiles/{id}/history` - Watch history
- `DELETE /profiles/{id}/watches/{title_id}` - Remove watch

### Lists
- `GET /profiles/{id}/lists` - Get lists
- `POST /profiles/{id}/lists` - Create list
- `POST /profiles/{id}/lists/{id}/items` - Add movie to list

### Recommendations
- `POST /profiles/{id}/recommend` - Get recommendations
- `GET /profiles/{id}/taste` - Taste profile status

### Onboarding
- `GET /profiles/{id}/onboarding-movies` - Get movies to rate
- `POST /profiles/{id}/onboarding-complete` - Mark onboarding done

## Data Sources

- **IMDb** - Movie catalog (titles, ratings, cast, crew)
- **OpenAI** - Text embeddings for taste matching
- **TMDb** - Poster images

## License

MIT
