from datetime import datetime

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    name: str


class ProfileUpdate(BaseModel):
    name: str


class ProfileResponse(BaseModel):
    id: int
    name: str
    onboarding_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
