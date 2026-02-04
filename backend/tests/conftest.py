import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.dependencies import get_db
from app.database import Base
from app.main import app
from app.models import catalog, personal, user  # noqa: F401 - ensure models registered
from app.models.catalog import CatalogTitle

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
