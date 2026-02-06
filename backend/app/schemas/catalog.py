from pydantic import BaseModel


class TitleSearchResult(BaseModel):
    id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_url: str | None = None

    model_config = {"from_attributes": True}


class PaginatedSearchResponse(BaseModel):
    results: list[TitleSearchResult]
    total: int
    page: int
    limit: int


class PersonBrief(BaseModel):
    id: int
    imdb_nconst: str
    primary_name: str

    model_config = {"from_attributes": True}


class PrincipalResponse(BaseModel):
    ordering: int | None
    category: str | None
    job: str | None
    characters: str | None
    person: PersonBrief

    model_config = {"from_attributes": True}


class AkaResponse(BaseModel):
    localized_title: str | None
    region: str | None
    language: str | None
    is_original: bool | None

    model_config = {"from_attributes": True}


class RatingResponse(BaseModel):
    average_rating: float | None
    num_votes: int | None

    model_config = {"from_attributes": True}


class CrewResponse(BaseModel):
    director_nconsts: list[str] | None
    writer_nconsts: list[str] | None

    model_config = {"from_attributes": True}


class TitleDetailResponse(BaseModel):
    id: int
    imdb_tconst: str
    title_type: str | None
    primary_title: str
    original_title: str | None
    start_year: int | None
    end_year: int | None
    runtime_minutes: int | None
    genres: str | None
    poster_url: str | None = None
    rating: RatingResponse | None
    principals: list[PrincipalResponse]
    crew: CrewResponse | None
    akas: list[AkaResponse]

    model_config = {"from_attributes": True}
