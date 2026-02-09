import warnings

from pydantic_settings import BaseSettings

_DEFAULT_SECRET = "change-me-to-a-random-secret-key"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/moviebrain"
    SECRET_KEY: str = _DEFAULT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"

    OPENAI_API_KEY: str = ""
    TMDB_API_KEY: str = ""
    OMDB_API_KEY: str = ""
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    RECOMMEND_DEFAULT_LIMIT: int = 20
    RECOMMEND_MIN_RATED_MOVIES: int = 5
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    MOOD_BLEND_WEIGHT: float = 0.6
    RECENCY_BOOST: float = 0.2
    RECENCY_WINDOW_DAYS: int = 90
    POPULARITY_WEIGHT: float = 0.30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

if settings.SECRET_KEY == _DEFAULT_SECRET:
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            "SECRET_KEY must be changed from the default value in production. "
            "Set a strong random value via the SECRET_KEY environment variable."
        )
    warnings.warn(
        "SECRET_KEY is using the default placeholder value. "
        "Set a strong random value before deploying to production.",
        stacklevel=1,
    )
