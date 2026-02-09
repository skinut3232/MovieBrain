import logging

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_db, get_verified_profile
from app.models.user import Profile
from app.schemas.recommend import (
    RecommendedTitle,
    RecommendRequest,
    RecommendResponse,
    TasteProfileResponse,
)
from app.services.recommender import (
    blend_vectors,
    compute_taste_vector,
    embed_mood_text,
    generate_mood_description,
    get_recommendations,
    get_user_top_movies,
    lookup_titles_in_catalog,
    suggest_mood_titles,
    _get_existing_taste,
)
from app.services.tmdb import get_poster_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles/{profile_id}", tags=["recommend"])

MODEL_ID = settings.EMBEDDING_MODEL


@router.post("/recommend", response_model=RecommendResponse)
def recommend(
    body: RecommendRequest,
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    """Get movie recommendations for a profile with optional filters."""
    search_vector = None
    mood_mode = False
    llm_picks: list = []

    mood_text = (body.mood or "").strip()
    if mood_text:
        try:
            top_movies = get_user_top_movies(db, profile.id)

            # Phase 1: Ask LLM for specific movie titles (the obvious picks)
            suggestions = suggest_mood_titles(mood_text, top_movies)
            logger.info("LLM suggested %d titles for mood '%s'", len(suggestions), mood_text)

            # Build exclusion set for catalog lookup
            from sqlalchemy import text as sa_text
            excluded_ids = {
                row[0]
                for row in db.execute(
                    sa_text("""
                        SELECT title_id FROM watches WHERE profile_id = :pid
                        UNION
                        SELECT title_id FROM movie_flags WHERE profile_id = :pid
                    """),
                    {"pid": profile.id},
                )
            }

            llm_picks = lookup_titles_in_catalog(db, suggestions, excluded_ids)
            logger.info("Matched %d LLM picks in catalog", len(llm_picks))

            # Phase 2: Also do embedding search for discovery picks
            description = generate_mood_description(mood_text, top_movies)
            logger.info("Mood description for '%s': %s", mood_text, description)
            mood_vec = embed_mood_text(description)

            taste = _get_existing_taste(db, profile.id, MODEL_ID)
            if taste is not None:
                tv = taste.taste_vector
                if isinstance(tv, str):
                    tv = np.fromstring(tv.strip("[]"), sep=",").tolist()
                search_vector = blend_vectors(mood_vec, tv)
            else:
                search_vector = mood_vec

            mood_mode = True
        except Exception as exc:
            logger.error("Mood search failed: %s", exc)
            raise HTTPException(
                status_code=503,
                detail="Mood search is temporarily unavailable. Please try again.",
            ) from exc

    result = get_recommendations(
        db=db,
        profile_id=profile.id,
        genre=body.genre,
        min_year=body.min_year,
        max_year=body.max_year,
        min_runtime=body.min_runtime,
        max_runtime=body.max_runtime,
        min_imdb_rating=body.min_imdb_rating,
        min_votes=body.min_votes,
        limit=body.limit,
        page=body.page,
        search_vector=search_vector,
    )

    # Merge: LLM picks first, then embedding discovery (deduplicated)
    if llm_picks:
        llm_pick_ids = {r.title_id for r in llm_picks}
        embedding_results = [r for r in result.results if r.title_id not in llm_pick_ids]
        # Fill up to the requested limit
        merged = llm_picks + embedding_results
        merged = merged[: body.limit]
    else:
        merged = result.results

    return RecommendResponse(
        results=[
            RecommendedTitle(
                title_id=r.title_id,
                imdb_tconst=r.imdb_tconst,
                primary_title=r.primary_title,
                start_year=r.start_year,
                runtime_minutes=r.runtime_minutes,
                genres=r.genres,
                average_rating=r.average_rating,
                num_votes=r.num_votes,
                similarity_score=r.similarity_score,
                poster_url=get_poster_url(r.poster_path),
                rt_critic_score=r.rt_critic_score,
            )
            for r in merged
        ],
        total=result.total,
        page=result.page,
        limit=result.limit,
        fallback_mode=result.fallback_mode,
        mood_mode=mood_mode,
    )


@router.get("/taste", response_model=TasteProfileResponse)
def taste_profile(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    """Get the taste profile status for a profile."""
    taste = _get_existing_taste(db, profile.id, MODEL_ID)

    # Count rated movies with embeddings
    from sqlalchemy import text

    count = db.execute(
        text("""
            SELECT COUNT(*)
            FROM watches w
            JOIN movie_embeddings me ON me.title_id = w.title_id AND me.model_id = :model_id
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
        """),
        {"profile_id": profile.id, "model_id": MODEL_ID},
    ).scalar()

    return TasteProfileResponse(
        has_taste_vector=taste is not None,
        num_rated_movies=count or 0,
        min_required=settings.RECOMMEND_MIN_RATED_MOVIES,
        updated_at=taste.updated_at if taste else None,
    )


@router.post("/taste/recompute", response_model=TasteProfileResponse)
def recompute_taste(
    profile: Profile = Depends(get_verified_profile),
    db: Session = Depends(get_db),
):
    """Force recomputation of the taste vector."""
    taste = compute_taste_vector(db, profile.id, MODEL_ID)

    from sqlalchemy import text

    count = db.execute(
        text("""
            SELECT COUNT(*)
            FROM watches w
            JOIN movie_embeddings me ON me.title_id = w.title_id AND me.model_id = :model_id
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
        """),
        {"profile_id": profile.id, "model_id": MODEL_ID},
    ).scalar()

    return TasteProfileResponse(
        has_taste_vector=taste is not None,
        num_rated_movies=count or 0,
        min_required=settings.RECOMMEND_MIN_RATED_MOVIES,
        updated_at=taste.updated_at if taste else None,
    )
