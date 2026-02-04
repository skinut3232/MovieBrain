from datetime import date, datetime

from pydantic import BaseModel, Field


class WatchCreate(BaseModel):
    title_id: int
    rating_1_10: int | None = Field(None, ge=1, le=10)
    notes: str | None = Field(None, max_length=4096)
    rewatch_count: int = 0
    watched_date: date | None = None
    tag_names: list[str] = []


class WatchUpdate(BaseModel):
    rating_1_10: int | None = Field(None, ge=1, le=10)
    notes: str | None = Field(None, max_length=4096)
    rewatch_count: int | None = None
    watched_date: date | None = None
    tag_names: list[str] | None = None


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TitleBrief(BaseModel):
    id: int
    primary_title: str
    start_year: int | None
    genres: str | None

    model_config = {"from_attributes": True}


class WatchResponse(BaseModel):
    id: int
    title_id: int
    rating_1_10: int | None
    notes: str | None
    rewatch_count: int
    watched_date: date | None
    created_at: datetime
    updated_at: datetime
    title: TitleBrief
    tags: list[TagResponse]

    model_config = {"from_attributes": True}


class PaginatedWatchHistory(BaseModel):
    results: list[WatchResponse]
    total: int
    page: int
    limit: int


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
