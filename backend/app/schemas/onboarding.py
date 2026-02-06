from pydantic import BaseModel


class OnboardingMovieResponse(BaseModel):
    title_id: int
    primary_title: str
    start_year: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_url: str | None = None

    model_config = {"from_attributes": True}


class OnboardingMoviesResponse(BaseModel):
    movies: list[OnboardingMovieResponse]
    remaining: int
