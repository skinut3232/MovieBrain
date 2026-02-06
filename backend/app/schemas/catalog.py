from typing import Literal

from pydantic import BaseModel, Field


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
    overview: str | None = None
    trailer_key: str | None = None
    rating: RatingResponse | None
    principals: list[PrincipalResponse]
    crew: CrewResponse | None
    akas: list[AkaResponse]

    model_config = {"from_attributes": True}


# Browse/Discovery schemas
SortOption = Literal["popularity", "rating", "year_desc", "year_asc"]


class BrowseTitle(BaseModel):
    id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_url: str | None = None


class BrowseResponse(BaseModel):
    results: list[BrowseTitle]
    total: int
    page: int
    limit: int


class SimilarTitle(BaseModel):
    id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    similarity_score: float
    poster_url: str | None = None


class PersonDetailResponse(BaseModel):
    id: int
    imdb_nconst: str
    primary_name: str
    birth_year: int | None
    death_year: int | None


class FilmographyItem(BaseModel):
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    genres: str | None
    category: str
    characters: str | None
    average_rating: float | None
    num_votes: int | None
    poster_url: str | None = None


class PersonWithFilmography(BaseModel):
    person: PersonDetailResponse
    filmography: list[FilmographyItem]


class GenreListResponse(BaseModel):
    genres: list[str]


class DecadeListResponse(BaseModel):
    decades: list[int]


# Collection schemas
class CollectionBrief(BaseModel):
    id: int
    name: str
    description: str | None
    collection_type: str

    model_config = {"from_attributes": True}


class CollectionTitle(BaseModel):
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_url: str | None = None
    position: int | None = None


class CollectionDetailResponse(BaseModel):
    id: int
    name: str
    description: str | None
    collection_type: str
    results: list[CollectionTitle]
    total: int
    page: int
    limit: int
