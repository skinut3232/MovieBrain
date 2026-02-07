from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.catalog import (
    BrowseResponse,
    BrowseTitle,
    DecadeListResponse,
    FeaturedRow,
    FeaturedRowMovie,
    FeaturedRowsResponse,
    FilmographyItem,
    GenreListResponse,
    PaginatedSearchResponse,
    PersonDetailResponse,
    PersonWithFilmography,
    RandomMovieResponse,
    SimilarTitle,
    SortOption,
    TitleDetailResponse,
    TitleSearchResult,
)
from app.services.catalog import get_title_detail, search_titles
from app.services.discovery import (
    DECADES,
    FEATURED_GENRES,
    GENRES,
    browse_catalog,
    get_featured_rows,
    get_person_by_id,
    get_person_filmography,
    get_random_movie,
    get_similar_movies,
)
from app.services.tmdb import get_or_fetch_movie_details, get_poster_url, refresh_trending_cache

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=PaginatedSearchResponse)
def search(
    q: str = Query(..., min_length=1),
    year: int | None = Query(None),
    genre: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=10),
    min_year: int | None = Query(None),
    max_year: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search titles with optional filters."""
    titles, total = search_titles(
        db, q,
        year=year,
        genre=genre,
        min_rating=min_rating,
        min_year=min_year,
        max_year=max_year,
        page=page,
        limit=limit,
    )

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


@router.get("/browse", response_model=BrowseResponse)
def browse(
    genre: str | None = Query(None),
    min_year: int | None = Query(None),
    max_year: int | None = Query(None),
    decade: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=10),
    sort_by: SortOption = Query("popularity"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    exclude_watched: int | None = Query(None, description="Profile ID to exclude watched movies"),
    db: Session = Depends(get_db),
):
    """Browse the catalog with filters and sorting."""
    results, total = browse_catalog(
        db,
        genre=genre,
        min_year=min_year,
        max_year=max_year,
        decade=decade,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        limit=limit,
        exclude_watched_profile_id=exclude_watched,
    )

    return BrowseResponse(
        results=[
            BrowseTitle(
                id=r.title_id,
                imdb_tconst=r.imdb_tconst,
                primary_title=r.primary_title,
                start_year=r.start_year,
                runtime_minutes=r.runtime_minutes,
                genres=r.genres,
                average_rating=r.average_rating,
                num_votes=r.num_votes,
                poster_url=get_poster_url(r.poster_path),
            )
            for r in results
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/random", response_model=RandomMovieResponse)
def random_movie(
    genre: str | None = Query(None),
    decade: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=10),
    exclude_watched: int | None = Query(None, description="Profile ID to exclude watched movies"),
    db: Session = Depends(get_db),
):
    """Get a random movie, optionally filtered by genre/decade/rating."""
    result = get_random_movie(
        db,
        genre=genre,
        decade=decade,
        min_rating=min_rating,
        exclude_watched_profile_id=exclude_watched,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found matching the criteria",
        )

    return RandomMovieResponse(
        id=result.title_id,
        imdb_tconst=result.imdb_tconst,
        primary_title=result.primary_title,
        start_year=result.start_year,
        runtime_minutes=result.runtime_minutes,
        genres=result.genres,
        average_rating=result.average_rating,
        num_votes=result.num_votes,
        poster_url=get_poster_url(result.poster_path),
        overview=result.overview,
    )


@router.get("/featured-rows", response_model=FeaturedRowsResponse)
def featured_rows(
    limit: int = Query(20, ge=1, le=50),
    exclude_watched: int | None = Query(None, description="Profile ID to exclude watched movies"),
    db: Session = Depends(get_db),
):
    """Get featured movie rows for the explore page."""
    rows = get_featured_rows(db, limit=limit, exclude_watched_profile_id=exclude_watched)

    return FeaturedRowsResponse(
        rows=[
            FeaturedRow(
                id=row.id,
                title=row.title,
                movies=[
                    FeaturedRowMovie(
                        id=m.title_id,
                        imdb_tconst=m.imdb_tconst,
                        primary_title=m.primary_title,
                        start_year=m.start_year,
                        runtime_minutes=m.runtime_minutes,
                        genres=m.genres,
                        average_rating=m.average_rating,
                        num_votes=m.num_votes,
                        poster_url=get_poster_url(m.poster_path),
                    )
                    for m in row.movies
                ],
            )
            for row in rows
        ]
    )


@router.get("/featured-genres")
def get_featured_genres():
    """Get list of featured genres for the explore page."""
    return {"genres": FEATURED_GENRES}


@router.get("/genres", response_model=GenreListResponse)
def get_genres():
    """Get list of available genres for browsing."""
    return GenreListResponse(genres=GENRES)


@router.get("/decades", response_model=DecadeListResponse)
def get_decades():
    """Get list of available decades for browsing."""
    return DecadeListResponse(decades=DECADES)


@router.get("/titles/{title_id}", response_model=TitleDetailResponse)
def get_title(title_id: int, db: Session = Depends(get_db)):
    title = get_title_detail(db, title_id)
    if not title:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    # Lazy-fill poster, overview, and trailer if needed
    details = get_or_fetch_movie_details(db, title)

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
        poster_url=get_poster_url(details["poster_path"]),
        overview=details["overview"],
        trailer_key=details["trailer_key"],
        rating=title.rating,
        principals=title.principals,
        crew=title.crew,
        akas=title.akas,
    )


@router.get("/titles/{title_id}/similar", response_model=list[SimilarTitle])
def get_similar(
    title_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get similar movies based on embedding similarity."""
    # First check if title exists
    title = get_title_detail(db, title_id)
    if not title:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    results = get_similar_movies(db, title_id, limit)

    return [
        SimilarTitle(
            id=r.title_id,
            imdb_tconst=r.imdb_tconst,
            primary_title=r.primary_title,
            start_year=r.start_year,
            runtime_minutes=r.runtime_minutes,
            genres=r.genres,
            average_rating=r.average_rating,
            num_votes=r.num_votes,
            similarity_score=r.similarity_score,
            poster_url=get_poster_url(r.poster_path),
        )
        for r in results
    ]


@router.get("/people/{person_id}", response_model=PersonWithFilmography)
def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get person details and filmography."""
    person = get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")

    filmography = get_person_filmography(db, person_id)

    return PersonWithFilmography(
        person=PersonDetailResponse(
            id=person.id,
            imdb_nconst=person.imdb_nconst,
            primary_name=person.primary_name,
            birth_year=person.birth_year,
            death_year=person.death_year,
        ),
        filmography=[
            FilmographyItem(
                title_id=f.title_id,
                imdb_tconst=f.imdb_tconst,
                primary_title=f.primary_title,
                start_year=f.start_year,
                genres=f.genres,
                category=f.category,
                characters=f.characters,
                average_rating=f.average_rating,
                num_votes=f.num_votes,
                poster_url=get_poster_url(f.poster_path),
            )
            for f in filmography
        ],
    )


@router.post("/trending/refresh")
def refresh_trending(db: Session = Depends(get_db)):
    """Manually refresh the trending cache from TMDB."""
    matched_count = refresh_trending_cache(db)
    return {"status": "refreshed", "matched_movies": matched_count}
