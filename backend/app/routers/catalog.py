from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.catalog import (
    BrowseResponse,
    BrowseTitle,
    DecadeListResponse,
    FeaturedRow,
    FeaturedRowMovie,
    FeaturedRowsResponse,
    FilmographyItem,
    GenreListResponse,
    LanguageListResponse,
    LanguageOption,
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
    get_available_languages,
    get_featured_rows,
    get_person_by_id,
    get_person_filmography,
    get_random_movie,
    get_similar_movies,
)
from app.services.omdb import get_or_fetch_omdb_ratings
from app.services.tmdb import (
    get_or_fetch_movie_details,
    get_or_fetch_watch_providers,
    get_poster_url,
    refresh_provider_master,
    refresh_trending_cache,
)

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
    genres: str | None = Query(None, description="Comma-separated genre list (OR logic)"),
    min_year: int | None = Query(None),
    max_year: int | None = Query(None),
    decade: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=10),
    min_rt_score: int | None = Query(None, ge=0, le=100),
    min_runtime: int | None = Query(None, ge=0),
    max_runtime: int | None = Query(None, ge=0),
    language: str | None = Query(None),
    provider_ids: str | None = Query(None, description="Comma-separated provider IDs"),
    sort_by: SortOption = Query("popularity"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    exclude_watched: int | None = Query(None, description="Profile ID to exclude watched movies"),
    db: Session = Depends(get_db),
):
    """Browse the catalog with filters and sorting."""
    genres_list = [g.strip() for g in genres.split(",") if g.strip()] if genres else None
    try:
        provider_id_list = (
            [int(p.strip()) for p in provider_ids.split(",") if p.strip()]
            if provider_ids else None
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="provider_ids must be a comma-separated list of integers",
        )

    results, total = browse_catalog(
        db,
        genre=genre,
        genres=genres_list,
        min_year=min_year,
        max_year=max_year,
        decade=decade,
        min_rating=min_rating,
        min_rt_score=min_rt_score,
        min_runtime=min_runtime,
        max_runtime=max_runtime,
        language=language,
        provider_ids=provider_id_list,
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
                rt_critic_score=r.rt_critic_score,
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
                        rt_critic_score=m.rt_critic_score,
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


@router.get("/languages", response_model=LanguageListResponse)
def get_languages(db: Session = Depends(get_db)):
    """Get list of available languages with movie counts."""
    languages = get_available_languages(db)
    return LanguageListResponse(
        languages=[
            LanguageOption(code=lang.code, count=lang.count)
            for lang in languages
        ]
    )


@router.get("/titles/{title_id}", response_model=TitleDetailResponse)
def get_title(title_id: int, db: Session = Depends(get_db)):
    title = get_title_detail(db, title_id)
    if not title:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    # Lazy-fill poster, overview, and trailer if needed
    details = get_or_fetch_movie_details(db, title)

    # Lazy-fill RT + Metacritic scores from OMDb
    omdb_scores = get_or_fetch_omdb_ratings(db, title)

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
        rt_critic_score=omdb_scores["rt_critic_score"],
        rt_audience_score=omdb_scores["rt_audience_score"],
        metacritic_score=omdb_scores["metacritic_score"],
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
def refresh_trending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually refresh the trending cache from TMDB."""
    matched_count = refresh_trending_cache(db)
    return {"status": "refreshed", "matched_movies": matched_count}


@router.get("/providers")
def get_providers(db: Session = Depends(get_db)):
    """Get streaming providers (flatrate only) with cached movie counts."""
    from sqlalchemy import func as sa_func
    from app.models.catalog import ProviderMaster, WatchProvider as WPModel

    # Only return streaming (flatrate) providers that have cached movies
    results = (
        db.query(
            ProviderMaster.provider_id,
            ProviderMaster.provider_name,
            ProviderMaster.logo_path,
            ProviderMaster.display_priority,
            sa_func.count(sa_func.distinct(WPModel.title_id)).label("movie_count"),
        )
        .join(WPModel, WPModel.provider_id == ProviderMaster.provider_id)
        .filter(WPModel.provider_type == "flatrate")
        .group_by(
            ProviderMaster.provider_id,
            ProviderMaster.provider_name,
            ProviderMaster.logo_path,
            ProviderMaster.display_priority,
        )
        .order_by(sa_func.count(sa_func.distinct(WPModel.title_id)).desc())
        .all()
    )

    return {
        "providers": [
            {
                "provider_id": r[0],
                "provider_name": r[1],
                "logo_path": r[2],
                "display_priority": r[3],
                "movie_count": r[4],
            }
            for r in results
        ]
    }


@router.get("/titles/{title_id}/providers")
def get_title_providers(title_id: int, db: Session = Depends(get_db)):
    """Get streaming providers for a specific movie (lazy-fetches from TMDB if needed)."""
    from app.services.catalog import get_title_detail as _get_title

    title = _get_title(db, title_id)
    if not title:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    providers = get_or_fetch_watch_providers(db, title)

    # Only return flatrate (subscription streaming) providers
    return [
        {
            "id": wp.id,
            "provider_id": wp.provider_id,
            "provider_name": wp.provider_name,
            "logo_path": wp.logo_path,
            "provider_type": wp.provider_type,
            "region": wp.region,
            "display_priority": wp.display_priority,
        }
        for wp in providers
        if wp.provider_type == "flatrate"
    ]


@router.post("/providers/refresh")
def refresh_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually refresh the provider master list from TMDB."""
    count = refresh_provider_master(db)
    return {"status": "refreshed", "providers_updated": count}
