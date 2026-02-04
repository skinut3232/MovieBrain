from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_verified_profile
from app.models.personal import ListItem, MovieList
from app.models.user import Profile
from app.schemas.list import (
    ListCreate,
    ListDetailResponse,
    ListItemAdd,
    ListItemReorder,
    ListItemResponse,
    ListResponse,
    ListUpdate,
)
from app.services.list import (
    add_list_item,
    create_list,
    delete_list,
    get_list_detail,
    get_lists,
    remove_list_item,
    reorder_list_items,
)

router = APIRouter(prefix="/profiles/{profile_id}/lists", tags=["lists"])


def _get_owned_list(
    list_id: int, profile: Profile, db: Session
) -> MovieList:
    movie_list = (
        db.query(MovieList)
        .filter(MovieList.id == list_id, MovieList.profile_id == profile.id)
        .first()
    )
    if not movie_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="List not found"
        )
    return movie_list


@router.get("", response_model=list[ListResponse])
def list_all_lists(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    return get_lists(db, profile.id)


@router.post("", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
def create_new_list(
    body: ListCreate,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    movie_list = create_list(db, profile.id, body.name, body.list_type)
    return ListResponse(
        id=movie_list.id,
        name=movie_list.name,
        list_type=movie_list.list_type,
        created_at=movie_list.created_at,
        updated_at=movie_list.updated_at,
        item_count=0,
    )


@router.get("/{list_id}", response_model=ListDetailResponse)
def get_list(
    list_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    _get_owned_list(list_id, profile, db)
    detail = get_list_detail(db, list_id)
    return detail


@router.patch("/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    body: ListUpdate,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    movie_list = _get_owned_list(list_id, profile, db)
    movie_list.name = body.name
    db.commit()
    db.refresh(movie_list)
    item_count = db.query(ListItem).filter(ListItem.list_id == list_id).count()
    return ListResponse(
        id=movie_list.id,
        name=movie_list.name,
        list_type=movie_list.list_type,
        created_at=movie_list.created_at,
        updated_at=movie_list.updated_at,
        item_count=item_count,
    )


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_list(
    list_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    movie_list = _get_owned_list(list_id, profile, db)
    delete_list(db, movie_list)


@router.post(
    "/{list_id}/items",
    response_model=ListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item(
    list_id: int,
    body: ListItemAdd,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    _get_owned_list(list_id, profile, db)
    # Check for duplicate
    existing = (
        db.query(ListItem)
        .filter(ListItem.list_id == list_id, ListItem.title_id == body.title_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Title already in list",
        )
    item = add_list_item(db, list_id, body.title_id, body.priority)
    # Reload with title relationship
    item = (
        db.query(ListItem)
        .filter(ListItem.id == item.id)
        .first()
    )
    return item


@router.patch("/{list_id}/items/reorder", status_code=status.HTTP_200_OK)
def reorder_items(
    list_id: int,
    body: ListItemReorder,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    _get_owned_list(list_id, profile, db)
    reorder_list_items(db, list_id, body.ordered_title_ids)
    return {"status": "ok"}


@router.delete(
    "/{list_id}/items/{title_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_item(
    list_id: int,
    title_id: int,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    _get_owned_list(list_id, profile, db)
    removed = remove_list_item(db, list_id, title_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in list",
        )
