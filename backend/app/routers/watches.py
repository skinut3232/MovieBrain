from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_verified_profile
from app.models.personal import Tag, Watch
from app.models.user import Profile
from app.schemas.watch import (
    PaginatedWatchHistory,
    TagCreate,
    TagResponse,
    WatchCreate,
    WatchResponse,
    WatchUpdate,
)
from app.services.watch import (
    create_or_update_watch,
    create_tag,
    delete_tag,
    delete_watch,
    get_profile_tags,
    get_watch_by_title,
    get_watch_history,
    update_watch,
)

router = APIRouter(prefix="/profiles/{profile_id}", tags=["watches"])


@router.post("/watches", response_model=WatchResponse)
def log_watch(
    body: WatchCreate,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    watch, is_new = create_or_update_watch(
        db=db,
        profile_id=profile.id,
        title_id=body.title_id,
        rating_1_10=body.rating_1_10,
        notes=body.notes,
        rewatch_count=body.rewatch_count,
        watched_date=body.watched_date,
        tag_names=body.tag_names,
    )
    # Reload with relationships
    watch = get_watch_by_title(db, profile.id, body.title_id)
    if is_new:
        from starlette.responses import JSONResponse
        return JSONResponse(
            content=WatchResponse.model_validate(watch).model_dump(mode="json"),
            status_code=status.HTTP_201_CREATED,
        )
    return watch


@router.get("/history", response_model=PaginatedWatchHistory)
def list_history(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["watched_date", "rating", "created_at"] = Query("watched_date"),
    tag: str | None = Query(None),
    min_rating: int | None = Query(None, ge=1, le=10),
    max_rating: int | None = Query(None, ge=1, le=10),
):
    results, total = get_watch_history(
        db,
        profile_id=profile.id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        tag=tag,
        min_rating=min_rating,
        max_rating=max_rating,
    )
    return PaginatedWatchHistory(
        results=results, total=total, page=page, limit=limit
    )


@router.delete(
    "/watches/{title_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_watch(
    title_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    watch = (
        db.query(Watch)
        .filter(Watch.profile_id == profile.id, Watch.title_id == title_id)
        .first()
    )
    if not watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Watch not found"
        )
    delete_watch(db, watch)


@router.get("/tags", response_model=list[TagResponse])
def list_tags(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    return get_profile_tags(db, profile.id)


@router.post(
    "/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED
)
def add_tag(
    body: TagCreate,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Tag)
        .filter(Tag.profile_id == profile.id, Tag.name == body.name.strip())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists",
        )
    return create_tag(db, profile.id, body.name)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag(
    tag_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id, Tag.profile_id == profile.id)
        .first()
    )
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    delete_tag(db, tag)
