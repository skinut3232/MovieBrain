import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.dependencies import get_db
from app.database import Base
from app.main import app
from app.models import catalog, user  # noqa: F401 - ensure models registered

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
