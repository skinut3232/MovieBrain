from datetime import datetime

from pydantic import BaseModel, Field

from app.models.personal import ListType


class ListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    list_type: ListType = ListType.custom


class ListUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ListItemAdd(BaseModel):
    title_id: int
    priority: int | None = Field(None, ge=1, le=5)


class ListItemReorder(BaseModel):
    ordered_title_ids: list[int]


class TitleBrief(BaseModel):
    id: int
    primary_title: str
    start_year: int | None
    genres: str | None

    model_config = {"from_attributes": True}


class ListItemResponse(BaseModel):
    title_id: int
    position: int
    priority: int | None
    added_at: datetime
    title: TitleBrief

    model_config = {"from_attributes": True}


class ListResponse(BaseModel):
    id: int
    name: str
    list_type: ListType
    created_at: datetime
    updated_at: datetime
    item_count: int

    model_config = {"from_attributes": True}


class ListDetailResponse(BaseModel):
    id: int
    name: str
    list_type: ListType
    created_at: datetime
    updated_at: datetime
    items: list[ListItemResponse]

    model_config = {"from_attributes": True}
