from dataclasses import dataclass

import numpy as np
from openai import OpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models.recommender import ProfileTaste

MODEL_ID = settings.EMBEDDING_MODEL
MIN_RATED = settings.RECOMMEND_MIN_RATED_MOVIES

_openai_client: OpenAI | None = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


@dataclass
class RecommendationResult:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    similarity_score: float | None
    poster_path: str | None = None
    rt_critic_score: int | None = None


@dataclass
class RecommendResponse:
    results: list[RecommendationResult]
    total: int
    page: int
    limit: int
    fallback_mode: bool


def compute_taste_vector(
    db: Session, profile_id: int, model_id: str = MODEL_ID
) -> ProfileTaste | None:
    """Compute a weighted average taste vector from a profile's rated movies.

    Weight = rating value. L2-normalizes the result.
    Returns None if fewer than MIN_RATED rated movies have embeddings.
    """
    rows = db.execute(
        text("""
            SELECT me.embedding, w.rating_1_10
            FROM watches w
            JOIN movie_embeddings me ON me.title_id = w.title_id AND me.model_id = :model_id
            WHERE w.profile_id = :profile_id
              AND w.rating_1_10 IS NOT NULL
        """),
        {"profile_id": profile_id, "model_id": model_id},
    ).fetchall()

    if len(rows) < MIN_RATED:
        return None

    embeddings = []
    weights = []
    for row in rows:
        vec_str = row[0]
        rating = row[1]
        if vec_str is None:
            continue
        # pgvector returns the vector as a string like "[0.1,0.2,...]"
        if isinstance(vec_str, str):
            vec = np.fromstring(vec_str.strip("[]"), sep=",", dtype=np.float32)
        else:
            vec = np.array(vec_str, dtype=np.float32)
        embeddings.append(vec)
        weights.append(float(rating))

    if len(embeddings) < MIN_RATED:
        return None

    embeddings_arr = np.array(embeddings)
    weights_arr = np.array(weights).reshape(-1, 1)

    taste = np.sum(embeddings_arr * weights_arr, axis=0)
    norm = np.linalg.norm(taste)
    if norm > 0:
        taste = taste / norm

    taste_list = taste.tolist()
    vec_str = "[" + ",".join(str(x) for x in taste_list) + "]"

    # Upsert into profile_taste
    db.execute(
        text("""
            INSERT INTO profile_taste (profile_id, model_id, taste_vector, num_rated_movies, updated_at)
            VALUES (:profile_id, :model_id, :taste_vector, :num_rated, now())
            ON CONFLICT (profile_id, model_id)
            DO UPDATE SET taste_vector = :taste_vector, num_rated_movies = :num_rated, updated_at = now()
        """),
        {
            "profile_id": profile_id,
            "model_id": model_id,
            "taste_vector": vec_str,
            "num_rated": len(embeddings),
        },
    )
    db.commit()

    return db.query(ProfileTaste).filter(
        ProfileTaste.profile_id == profile_id,
        ProfileTaste.model_id == model_id,
    ).first()


def _get_existing_taste(db: Session, profile_id: int, model_id: str = MODEL_ID) -> ProfileTaste | None:
    """Get existing taste vector if it exists."""
    return db.query(ProfileTaste).filter(
        ProfileTaste.profile_id == profile_id,
        ProfileTaste.model_id == model_id,
    ).first()


def _get_latest_watch_time(db: Session, profile_id: int):
    """Get the latest watch updated_at for staleness check."""
    row = db.execute(
        text("""
            SELECT MAX(w.updated_at) FROM watches w
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
        """),
        {"profile_id": profile_id},
    ).fetchone()
    return row[0] if row else None


def get_user_top_movies(db: Session, profile_id: int, n: int = 10) -> list[dict]:
    """Get a user's top-rated movies for LLM context."""
    rows = db.execute(
        text("""
            SELECT ct.primary_title, ct.start_year, ct.genres, w.rating_1_10
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
            ORDER BY w.rating_1_10 DESC, w.updated_at DESC
            LIMIT :n
        """),
        {"profile_id": profile_id, "n": n},
    ).fetchall()
    return [
        {"title": r[0], "year": r[1], "genres": r[2], "rating": r[3]}
        for r in rows
    ]


def generate_mood_description(mood_text: str, top_movies: list[dict]) -> str:
    """Use GPT-4o-mini to generate an ideal movie description from mood + taste context."""
    client = _get_openai_client()

    movies_context = ""
    if top_movies:
        lines = []
        for m in top_movies:
            year = f" ({m['year']})" if m['year'] else ""
            genres = f" [{m['genres']}]" if m['genres'] else ""
            lines.append(f"- {m['title']}{year}{genres} — rated {m['rating']}/10")
        movies_context = "\n\nUser's top-rated movies:\n" + "\n".join(lines)

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a movie recommendation assistant. Given a user's mood request "
                    "and their favorite movies, describe the ideal movie they'd want to watch. "
                    "Include genre, tone, era, pacing, and type of story. "
                    "Write 2-3 sentences in the style of a movie description. "
                    "Do NOT name specific real movies."
                ),
            },
            {
                "role": "user",
                "content": f"Mood: {mood_text}{movies_context}",
            },
        ],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content or mood_text


def embed_mood_text(text: str) -> list[float]:
    """Embed mood description text using the same model as movie embeddings."""
    client = _get_openai_client()
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def blend_vectors(
    mood_vec: list[float],
    taste_vec: list[float],
    mood_weight: float = settings.MOOD_BLEND_WEIGHT,
) -> list[float]:
    """Weighted average of mood and taste vectors, L2-normalized."""
    mood_arr = np.array(mood_vec, dtype=np.float64)
    taste_arr = np.array(taste_vec, dtype=np.float64)
    blended = mood_weight * mood_arr + (1 - mood_weight) * taste_arr
    norm = np.linalg.norm(blended)
    if norm > 0:
        blended = blended / norm
    return blended.tolist()


def get_recommendations(
    db: Session,
    profile_id: int,
    genre: str | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    min_runtime: int | None = None,
    max_runtime: int | None = None,
    min_imdb_rating: float | None = None,
    min_votes: int | None = None,
    limit: int = 20,
    page: int = 1,
    search_vector: list[float] | None = None,
) -> RecommendResponse:
    """Get movie recommendations for a profile.

    When search_vector is provided, uses it directly for similarity search
    (used for mood-based recommendations). Otherwise uses the taste vector
    if available, falling back to popularity ranking.
    """
    offset = (page - 1) * limit

    if search_vector is not None:
        # Mood mode: use the provided search vector directly
        taste = None
        fallback_mode = False
    else:
        # Standard mode: lazy recompute taste vector
        taste = _get_existing_taste(db, profile_id)
        latest_watch = _get_latest_watch_time(db, profile_id)

        if taste is None or (latest_watch and taste.updated_at and latest_watch > taste.updated_at):
            taste = compute_taste_vector(db, profile_id)

        fallback_mode = taste is None

    # Build exclusion set: watched + flagged title_ids
    exclusion_query = text("""
        SELECT title_id FROM watches WHERE profile_id = :profile_id
        UNION
        SELECT title_id FROM movie_flags WHERE profile_id = :profile_id
    """)
    excluded_ids = {row[0] for row in db.execute(exclusion_query, {"profile_id": profile_id})}

    # Build filter conditions
    filters = []
    params: dict = {
        "profile_id": profile_id,
        "limit": limit,
        "offset": offset,
    }

    if genre:
        filters.append("ct.genres ILIKE :genre")
        params["genre"] = f"%{genre}%"
    if min_year is not None:
        filters.append("ct.start_year >= :min_year")
        params["min_year"] = min_year
    if max_year is not None:
        filters.append("ct.start_year <= :max_year")
        params["max_year"] = max_year
    if min_runtime is not None:
        filters.append("ct.runtime_minutes >= :min_runtime")
        params["min_runtime"] = min_runtime
    if max_runtime is not None:
        filters.append("ct.runtime_minutes <= :max_runtime")
        params["max_runtime"] = max_runtime
    if min_imdb_rating is not None:
        filters.append("cr.average_rating >= :min_imdb_rating")
        params["min_imdb_rating"] = min_imdb_rating
    if min_votes is not None:
        filters.append("cr.num_votes >= :min_votes")
        params["min_votes"] = min_votes

    # Always exclude already-watched/flagged movies
    if excluded_ids:
        filters.append("ct.id != ALL(:excluded_ids)")
        params["excluded_ids"] = list(excluded_ids)

    where_clause = " AND ".join(filters) if filters else "TRUE"

    if search_vector is not None or not fallback_mode:
        # Vector similarity search (mood vector or taste vector)
        if search_vector is not None:
            vec_list = search_vector
        else:
            tv = taste.taste_vector
            if isinstance(tv, str):
                tv = np.fromstring(tv.strip("[]"), sep=",").tolist()
            vec_list = tv
        taste_vec_str = "[" + ",".join(str(float(x)) for x in vec_list) + "]"
        params["taste_vector"] = taste_vec_str
        params["model_id"] = MODEL_ID

        count_sql = text(f"""
            SELECT COUNT(*)
            FROM movie_embeddings me
            JOIN catalog_titles ct ON ct.id = me.title_id
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE me.model_id = :model_id AND {where_clause}
        """)
        total = db.execute(count_sql, params).scalar()

        query_sql = text(f"""
            SELECT
                ct.id AS title_id,
                ct.imdb_tconst,
                ct.primary_title,
                ct.start_year,
                ct.runtime_minutes,
                ct.genres,
                cr.average_rating,
                cr.num_votes,
                1 - (me.embedding <=> CAST(:taste_vector AS vector)) AS similarity_score,
                ct.poster_path,
                cr.rt_critic_score
            FROM movie_embeddings me
            JOIN catalog_titles ct ON ct.id = me.title_id
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE me.model_id = :model_id AND {where_clause}
            ORDER BY me.embedding <=> CAST(:taste_vector AS vector) ASC
            LIMIT :limit OFFSET :offset
        """)
    else:
        # Fallback: popularity ranking
        count_sql = text(f"""
            SELECT COUNT(*)
            FROM catalog_titles ct
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE {where_clause}
        """)
        total = db.execute(count_sql, params).scalar()

        query_sql = text(f"""
            SELECT
                ct.id AS title_id,
                ct.imdb_tconst,
                ct.primary_title,
                ct.start_year,
                ct.runtime_minutes,
                ct.genres,
                cr.average_rating,
                cr.num_votes,
                NULL AS similarity_score,
                ct.poster_path,
                cr.rt_critic_score
            FROM catalog_titles ct
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE {where_clause}
            ORDER BY cr.average_rating * LN(cr.num_votes + 1) DESC
            LIMIT :limit OFFSET :offset
        """)

    rows = db.execute(query_sql, params).fetchall()

    results = [
        RecommendationResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            similarity_score=round(row[8], 4) if row[8] is not None else None,
            poster_path=row[9],
            rt_critic_score=row[10],
        )
        for row in rows
    ]

    return RecommendResponse(
        results=results,
        total=total or 0,
        page=page,
        limit=limit,
        fallback_mode=fallback_mode,
    )
