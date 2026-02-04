from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_verified_profile
from app.models.personal import FlagType
from app.models.user import Profile
from app.schemas.flag import FlagCreate, FlagResponse
from app.services.flag import create_flag, delete_flag, get_flags

router = APIRouter(prefix="/profiles/{profile_id}", tags=["flags"])


@router.post("/flags", response_model=FlagResponse, status_code=status.HTTP_201_CREATED)
def add_flag(
    body: FlagCreate,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    flag = create_flag(db, profile.id, body.title_id, body.flag_type)
    return flag


@router.delete("/flags/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_flag(
    title_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    removed = delete_flag(db, profile.id, title_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flag not found",
        )


@router.get("/flags", response_model=list[FlagResponse])
def list_flags(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
    flag_type: FlagType | None = Query(None),
):
    return get_flags(db, profile.id, flag_type)
