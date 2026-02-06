from datetime import datetime

from pydantic import BaseModel, Field

from app.config import settings


class RecommendRequest(BaseModel):
    genre: str | None = None
    min_year: int | None = None
    max_year: int | None = None
    min_runtime: int | None = None
    max_runtime: int | None = None
    min_imdb_rating: float | None = Field(None, ge=0, le=10)
    min_votes: int | None = Field(None, ge=0)
    limit: int = Field(settings.RECOMMEND_DEFAULT_LIMIT, ge=1, le=100)
    page: int = Field(1, ge=1)


class RecommendedTitle(BaseModel):
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    similarity_score: float | None
    poster_url: str | None = None


class RecommendResponse(BaseModel):
    results: list[RecommendedTitle]
    total: int
    page: int
    limit: int
    fallback_mode: bool


class TasteProfileResponse(BaseModel):
    has_taste_vector: bool
    num_rated_movies: int
    min_required: int
    updated_at: datetime | None
