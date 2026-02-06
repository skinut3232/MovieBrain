from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.catalog import PaginatedSearchResponse, TitleDetailResponse, TitleSearchResult
from app.services.catalog import get_title_detail, search_titles
from app.services.tmdb import get_or_fetch_poster_path, get_poster_url

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=PaginatedSearchResponse)
def search(
    q: str = Query(..., min_length=1),
    year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    titles, total = search_titles(db, q, year=year, page=page, limit=limit)

    results = []
    for title in titles:
        rating = title.rating
        results.append(
            TitleSearchResult(
                id=title.id,
                imdb_tconst=title.imdb_tconst,
                primary_title=title.primary_title,
                start_year=title.start_year,
                runtime_minutes=title.runtime_minutes,
                genres=title.genres,
                average_rating=rating.average_rating if rating else None,
                num_votes=rating.num_votes if rating else None,
                poster_url=get_poster_url(title.poster_path),
            )
        )

    return PaginatedSearchResponse(results=results, total=total, page=page, limit=limit)


@router.get("/titles/{title_id}", response_model=TitleDetailResponse)
def get_title(title_id: int, db: Session = Depends(get_db)):
    title = get_title_detail(db, title_id)
    if not title:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    # Lazy-fill poster if needed
    poster_path = get_or_fetch_poster_path(db, title)

    return TitleDetailResponse(
        id=title.id,
        imdb_tconst=title.imdb_tconst,
        title_type=title.title_type,
        primary_title=title.primary_title,
        original_title=title.original_title,
        start_year=title.start_year,
        end_year=title.end_year,
        runtime_minutes=title.runtime_minutes,
        genres=title.genres,
        poster_url=get_poster_url(poster_path),
        rating=title.rating,
        principals=title.principals,
        crew=title.crew,
        akas=title.akas,
    )
