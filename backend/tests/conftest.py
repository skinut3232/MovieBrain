import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.dependencies import get_db
from app.database import Base
from app.main import app
from app.models import catalog, personal, recommender, user  # noqa: F401 - ensure models registered
from app.models.catalog import CatalogRating, CatalogTitle

# Use a separate test database
TEST_DB_URL = settings.DATABASE_URL.rsplit("/", 1)[0] + "/moviebrain_test"

engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create the test database and tables once per test session."""
    # Connect to default postgres db to create test db
    default_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
    with default_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='moviebrain_test'")
        ).fetchone()
        if not result:
            conn.execute(text("CREATE DATABASE moviebrain_test"))
    default_engine.dispose()

    # Enable pgvector extension in test database (if available)
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        except Exception:
            conn.rollback()

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get a test database session, rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestSession(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """FastAPI test client with DB override scoped to a single test."""
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def auth_profile(client, db):
    """Register a user, create a profile, and return (headers, profile_id)."""
    reg = client.post(
        "/auth/register",
        json={"email": "fixture@example.com", "password": "testpass"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/profiles", json={"name": "Test Profile"}, headers=headers)
    profile_id = resp.json()["id"]

    return headers, profile_id


@pytest.fixture
def seed_movie(db):
    """Insert a catalog title for testing and return its id."""
    title = CatalogTitle(
        imdb_tconst="tt0000001",
        primary_title="Test Movie",
        original_title="Test Movie",
        title_type="movie",
        start_year=2020,
        runtime_minutes=120,
        genres="Drama",
    )
    db.add(title)
    db.flush()
    return title.id


@pytest.fixture
def seed_movies(db):
    """Insert multiple catalog titles for testing. Returns list of ids."""
    ids = []
    for i in range(3):
        title = CatalogTitle(
            imdb_tconst=f"tt000000{i + 1}",
            primary_title=f"Test Movie {i + 1}",
            original_title=f"Test Movie {i + 1}",
            title_type="movie",
            start_year=2020 + i,
            runtime_minutes=90 + i * 10,
            genres="Drama",
        )
        db.add(title)
        db.flush()
        ids.append(title.id)
    return ids


@pytest.fixture
def seed_movies_with_embeddings(db):
    """Insert movies with ratings and deterministic fake embeddings.

    Creates 10 movies with embeddings and ratings suitable for
    recommendation testing. Returns list of title ids.
    """
    import numpy as np

    model_id = "text-embedding-3-small"
    ids = []
    genres_list = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror",
                   "Action,Sci-Fi", "Comedy,Drama", "Drama,Horror", "Action", "Comedy"]

    for i in range(10):
        title = CatalogTitle(
            imdb_tconst=f"tt100000{i}",
            primary_title=f"Embed Movie {i}",
            original_title=f"Embed Movie {i}",
            title_type="movie",
            start_year=2000 + i,
            runtime_minutes=90 + i * 5,
            genres=genres_list[i],
        )
        db.add(title)
        db.flush()
        ids.append(title.id)

        # Add rating
        rating = CatalogRating(
            title_id=title.id,
            average_rating=5.0 + i * 0.5,
            num_votes=1000 + i * 500,
        )
        db.add(rating)
        db.flush()

        # Create a deterministic embedding vector
        rng = np.random.RandomState(seed=i)
        vec = rng.randn(1536).astype(np.float32)
        vec = vec / np.linalg.norm(vec)
        vec_str = "[" + ",".join(str(float(x)) for x in vec) + "]"

        db.execute(
            text("""
                INSERT INTO movie_embeddings (title_id, model_id, embedding, embedding_text, updated_at)
                VALUES (:title_id, :model_id, CAST(:embedding AS vector), :embedding_text, now())
            """),
            {
                "title_id": title.id,
                "model_id": model_id,
                "embedding": vec_str,
                "embedding_text": f"Embed Movie {i} ({2000 + i}). {genres_list[i]}.",
            },
        )

    db.flush()
    return ids
