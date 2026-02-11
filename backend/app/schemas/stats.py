from pydantic import BaseModel


class RatingBucket(BaseModel):
    rating: int
    count: int


class GenreCount(BaseModel):
    genre: str
    count: int


class PersonStat(BaseModel):
    person_id: int
    name: str
    count: int
    avg_rating: float | None


class CriticComparison(BaseModel):
    title_id: int
    primary_title: str
    user_score: float
    critic_score: float


class MonthCount(BaseModel):
    month: str
    count: int


class MonthRating(BaseModel):
    month: str
    avg_rating: float


class DecadeCount(BaseModel):
    decade: int
    count: int


class RatedMovie(BaseModel):
    title_id: int
    primary_title: str
    start_year: int | None
    rating: int
    poster_url: str | None


class LanguageCount(BaseModel):
    language: str
    count: int


class ProfileStats(BaseModel):
    total_movies: int = 0
    avg_rating: float | None = None
    total_runtime_minutes: int = 0
    unique_languages: int = 0
    total_rewatches: int = 0

    rating_distribution: list[RatingBucket] = []
    genre_breakdown: list[GenreCount] = []
    top_directors: list[PersonStat] = []
    top_actors: list[PersonStat] = []

    critic_comparisons: list[CriticComparison] = []
    avg_user_score: float | None = None
    avg_critic_score: float | None = None
    avg_difference: float | None = None

    movies_per_month: list[MonthCount] = []
    rating_over_time: list[MonthRating] = []
    decade_distribution: list[DecadeCount] = []

    highest_rated: list[RatedMovie] = []
    lowest_rated: list[RatedMovie] = []
    language_diversity: list[LanguageCount] = []
