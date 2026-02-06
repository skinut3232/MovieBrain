from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.catalog import (
    CollectionBrief,
    CollectionDetailResponse,
    CollectionTitle,
)
from app.services.collection import (
    get_all_collections,
    get_collection_by_id,
    get_collection_movies,
    seed_default_collections,
)
from app.services.tmdb import get_poster_url

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("", response_model=list[CollectionBrief])
def list_collections(db: Session = Depends(get_db)):
    """Get all available collections."""
    # Seed default collections if none exist
    collections = get_all_collections(db)
    if not collections:
        seed_default_collections(db)
        collections = get_all_collections(db)

    return [
        CollectionBrief(
            id=c.id,
            name=c.name,
            description=c.description,
            collection_type=c.collection_type,
        )
        for c in collections
    ]


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
def get_collection(
    collection_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get a collection with its movies."""
    collection = get_collection_by_id(db, collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    movies, total = get_collection_movies(db, collection, page, limit)

    return CollectionDetailResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        collection_type=collection.collection_type,
        results=[
            CollectionTitle(
                title_id=m.title_id,
                imdb_tconst=m.imdb_tconst,
                primary_title=m.primary_title,
                start_year=m.start_year,
                genres=m.genres,
                average_rating=m.average_rating,
                num_votes=m.num_votes,
                poster_url=get_poster_url(m.poster_path),
                position=m.position,
            )
            for m in movies
        ],
        total=total,
        page=page,
        limit=limit,
    )
