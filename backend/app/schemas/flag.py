from datetime import datetime

from pydantic import BaseModel

from app.models.personal import FlagType


class FlagCreate(BaseModel):
    title_id: int
    flag_type: FlagType


class FlagResponse(BaseModel):
    id: int
    title_id: int
    flag_type: FlagType
    created_at: datetime

    model_config = {"from_attributes": True}
