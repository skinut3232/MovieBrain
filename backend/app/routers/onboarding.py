from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_verified_profile
from app.models.user import Profile
from app.schemas.onboarding import OnboardingMovieResponse, OnboardingMoviesResponse
from app.services.tmdb import get_poster_url

router = APIRouter(prefix="/profiles/{profile_id}", tags=["onboarding"])


@router.get("/onboarding-movies", response_model=OnboardingMoviesResponse)
def get_onboarding_movies(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Return the next batch of onboarding movies the user hasn't rated yet."""
    rows = db.execute(
        text("""
            SELECT ct.id, ct.primary_title, ct.start_year, ct.genres,
                   cr.average_rating, cr.num_votes, ct.poster_path
            FROM onboarding_movies om
            JOIN catalog_titles ct ON ct.id = om.title_id
            LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE om.title_id NOT IN (
                SELECT w.title_id FROM watches w WHERE w.profile_id = :profile_id
            )
            ORDER BY om.display_order
            LIMIT :limit
        """),
        {"profile_id": profile.id, "limit": limit},
    ).fetchall()

    # Count total remaining
    remaining = db.execute(
        text("""
            SELECT COUNT(*)
            FROM onboarding_movies om
            WHERE om.title_id NOT IN (
                SELECT w.title_id FROM watches w WHERE w.profile_id = :profile_id
            )
        """),
        {"profile_id": profile.id},
    ).scalar()

    movies = [
        OnboardingMovieResponse(
            title_id=row[0],
            primary_title=row[1],
            start_year=row[2],
            genres=row[3],
            average_rating=row[4],
            num_votes=row[5],
            poster_url=get_poster_url(row[6]),
        )
        for row in rows
    ]

    return OnboardingMoviesResponse(movies=movies, remaining=remaining or 0)


@router.post("/onboarding-complete", status_code=status.HTTP_200_OK)
def complete_onboarding(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    """Mark onboarding as completed for this profile."""
    profile.onboarding_completed = True
    db.commit()
    return {"status": "ok"}
