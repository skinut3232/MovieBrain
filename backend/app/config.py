from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/moviebrain"
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENAI_API_KEY: str = ""
    TMDB_API_KEY: str = ""
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    RECOMMEND_DEFAULT_LIMIT: int = 20
    RECOMMEND_MIN_RATED_MOVIES: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
