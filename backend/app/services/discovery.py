from dataclasses import dataclass
import logging
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models.catalog import CatalogPerson, CatalogTitle

logger = logging.getLogger(__name__)

MODEL_ID = settings.EMBEDDING_MODEL


@dataclass
class BrowseResult:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_path: str | None
    rt_critic_score: int | None = None


@dataclass
class SimilarMovieResult:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    similarity_score: float
    poster_path: str | None


@dataclass
class PersonFilmography:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    genres: str | None
    category: str
    characters: str | None
    average_rating: float | None
    num_votes: int | None
    poster_path: str | None


SortOption = Literal["popularity", "rating", "year_desc", "year_asc"]


def browse_catalog(
    db: Session,
    genre: str | None = None,
    genres: list[str] | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    decade: int | None = None,
    min_rating: float | None = None,
    min_rt_score: int | None = None,
    min_runtime: int | None = None,
    max_runtime: int | None = None,
    language: str | None = None,
    provider_ids: list[int] | None = None,
    sort_by: SortOption = "popularity",
    page: int = 1,
    limit: int = 20,
    exclude_watched_profile_id: int | None = None,
) -> tuple[list[BrowseResult], int]:
    """Browse the catalog with filters and sorting."""
    offset = (page - 1) * limit

    filters = []
    params: dict = {"limit": limit, "offset": offset}

    # Exclude watched movies if profile_id is provided
    if exclude_watched_profile_id is not None:
        filters.append(
            "ct.id NOT IN (SELECT title_id FROM watches WHERE profile_id = :exclude_profile_id)"
        )
        params["exclude_profile_id"] = exclude_watched_profile_id

    # Apply decade filter (overrides min/max year if provided)
    if decade is not None:
        min_year = decade
        max_year = decade + 9

    # Multi-genre filter (OR logic) takes precedence over single genre
    if genres:
        genre_clauses = []
        for i, g in enumerate(genres):
            param_name = f"genre_{i}"
            genre_clauses.append(f"ct.genres ILIKE :{param_name}")
            params[param_name] = f"%{g}%"
        filters.append(f"({' OR '.join(genre_clauses)})")
    elif genre:
        filters.append("ct.genres ILIKE :genre")
        params["genre"] = f"%{genre}%"

    if min_year is not None:
        filters.append("ct.start_year >= :min_year")
        params["min_year"] = min_year
    if max_year is not None:
        filters.append("ct.start_year <= :max_year")
        params["max_year"] = max_year
    if min_rating is not None:
        filters.append("cr.average_rating >= :min_rating")  # This implicitly excludes NULLs
        params["min_rating"] = min_rating
    if min_rt_score is not None:
        filters.append("cr.rt_critic_score >= :min_rt_score")
        params["min_rt_score"] = min_rt_score
    if min_runtime is not None:
        filters.append("ct.runtime_minutes >= :min_runtime")
        params["min_runtime"] = min_runtime
    if max_runtime is not None:
        filters.append("ct.runtime_minutes <= :max_runtime")
        params["max_runtime"] = max_runtime
    if language is not None:
        filters.append("ct.original_language = :language")
        params["language"] = language
    if provider_ids:
        pid_placeholders = ", ".join(f":pid_{i}" for i in range(len(provider_ids)))
        for i, pid in enumerate(provider_ids):
            params[f"pid_{i}"] = pid
        filters.append(
            f"EXISTS (SELECT 1 FROM watch_providers wp WHERE wp.title_id = ct.id AND wp.provider_id IN ({pid_placeholders}) AND wp.provider_type = 'flatrate')"
        )

    where_clause = " AND ".join(filters) if filters else "TRUE"

    # Determine sort order (NULLS LAST for ratings since we use LEFT JOIN)
    sort_clauses = {
        "popularity": "COALESCE(cr.average_rating * LN(cr.num_votes + 1), 0) DESC",
        "rating": "cr.average_rating DESC NULLS LAST, cr.num_votes DESC NULLS LAST",
        "year_desc": "ct.start_year DESC NULLS LAST, cr.num_votes DESC NULLS LAST",
        "year_asc": "ct.start_year ASC NULLS LAST, cr.num_votes DESC NULLS LAST",
    }
    order_by = sort_clauses.get(sort_by, sort_clauses["popularity"])

    # Get total count
    count_sql = text(f"""
        SELECT COUNT(*)
        FROM catalog_titles ct
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
    """)
    total = db.execute(count_sql, params).scalar() or 0

    # Get results
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
            ct.poster_path,
            cr.rt_critic_score
        FROM catalog_titles ct
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(query_sql, params).fetchall()

    results = [
        BrowseResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            poster_path=row[8],
            rt_critic_score=row[9],
        )
        for row in rows
    ]

    return results, total


def get_similar_movies(
    db: Session,
    title_id: int,
    limit: int = 10,
) -> list[SimilarMovieResult]:
    """Get similar movies using embedding similarity."""
    # First check if the source movie has an embedding
    check_sql = text("""
        SELECT embedding FROM movie_embeddings
        WHERE title_id = :title_id AND model_id = :model_id
    """)
    result = db.execute(check_sql, {"title_id": title_id, "model_id": MODEL_ID}).fetchone()

    if not result or not result[0]:
        # No embedding, fall back to same-genre + similar year
        return _get_similar_by_metadata(db, title_id, limit)

    # Use vector similarity
    query_sql = text("""
        SELECT
            ct.id AS title_id,
            ct.imdb_tconst,
            ct.primary_title,
            ct.start_year,
            ct.runtime_minutes,
            ct.genres,
            cr.average_rating,
            cr.num_votes,
            1 - (me.embedding <=> (SELECT embedding FROM movie_embeddings WHERE title_id = :title_id AND model_id = :model_id)) AS similarity_score,
            ct.poster_path
        FROM movie_embeddings me
        JOIN catalog_titles ct ON ct.id = me.title_id
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE me.model_id = :model_id
          AND me.title_id != :title_id
        ORDER BY me.embedding <=> (SELECT embedding FROM movie_embeddings WHERE title_id = :title_id AND model_id = :model_id) ASC
        LIMIT :limit
    """)

    rows = db.execute(query_sql, {"title_id": title_id, "model_id": MODEL_ID, "limit": limit}).fetchall()

    return [
        SimilarMovieResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            similarity_score=round(row[8], 4) if row[8] else 0.0,
            poster_path=row[9],
        )
        for row in rows
    ]


def _get_similar_by_metadata(
    db: Session,
    title_id: int,
    limit: int,
) -> list[SimilarMovieResult]:
    """Fallback: find similar movies by genre and year when no embedding exists."""
    # Get source movie's metadata
    source = db.query(CatalogTitle).filter(CatalogTitle.id == title_id).first()
    if not source:
        return []

    filters = ["ct.id != :title_id"]
    params: dict = {"title_id": title_id, "limit": limit}

    # Match primary genre if available
    if source.genres:
        primary_genre = source.genres.split(",")[0].strip()
        filters.append("ct.genres ILIKE :genre")
        params["genre"] = f"%{primary_genre}%"

    # Similar year range (+/- 10 years)
    if source.start_year:
        filters.append("ct.start_year BETWEEN :min_year AND :max_year")
        params["min_year"] = source.start_year - 10
        params["max_year"] = source.start_year + 10

    where_clause = " AND ".join(filters)

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
            0.0 AS similarity_score,
            ct.poster_path
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY cr.average_rating * LN(cr.num_votes + 1) DESC
        LIMIT :limit
    """)

    rows = db.execute(query_sql, params).fetchall()

    return [
        SimilarMovieResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            similarity_score=0.0,  # No similarity score for metadata fallback
            poster_path=row[9],
        )
        for row in rows
    ]


def get_person_by_id(db: Session, person_id: int) -> CatalogPerson | None:
    """Get a person by their internal ID."""
    return db.query(CatalogPerson).filter(CatalogPerson.id == person_id).first()


def get_person_filmography(
    db: Session,
    person_id: int,
) -> list[PersonFilmography]:
    """Get a person's filmography with all their movie credits."""
    query_sql = text("""
        SELECT
            ct.id AS title_id,
            ct.imdb_tconst,
            ct.primary_title,
            ct.start_year,
            ct.genres,
            cp.category,
            cp.characters,
            cr.average_rating,
            cr.num_votes,
            ct.poster_path
        FROM catalog_principals cp
        JOIN catalog_titles ct ON ct.id = cp.title_id
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE cp.person_id = :person_id
        ORDER BY ct.start_year DESC NULLS LAST, cr.num_votes DESC NULLS LAST
    """)

    rows = db.execute(query_sql, {"person_id": person_id}).fetchall()

    return [
        PersonFilmography(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            genres=row[4],
            category=row[5],
            characters=row[6],
            average_rating=row[7],
            num_votes=row[8],
            poster_path=row[9],
        )
        for row in rows
    ]


# Predefined genre list for browsing
GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western",
]

DECADES = [1970, 1980, 1990, 2000, 2010, 2020]

# Featured genres for the explore page
FEATURED_GENRES = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Thriller"]


@dataclass
class RandomMovieResult:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    runtime_minutes: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_path: str | None
    overview: str | None


@dataclass
class FeaturedRow:
    id: str
    title: str
    movies: list[BrowseResult]


def get_random_movie(
    db: Session,
    genre: str | None = None,
    decade: int | None = None,
    min_rating: float | None = None,
    exclude_watched_profile_id: int | None = None,
) -> RandomMovieResult | None:
    """Get a random movie, optionally filtered by genre/decade/rating."""
    filters = ["cr.num_votes >= 1000"]  # Only include well-known movies
    params: dict = {}

    # Exclude watched movies if profile_id is provided
    if exclude_watched_profile_id is not None:
        filters.append(
            "ct.id NOT IN (SELECT title_id FROM watches WHERE profile_id = :exclude_profile_id)"
        )
        params["exclude_profile_id"] = exclude_watched_profile_id

    if genre:
        filters.append("ct.genres ILIKE :genre")
        params["genre"] = f"%{genre}%"

    if decade is not None:
        filters.append("ct.start_year >= :min_year AND ct.start_year <= :max_year")
        params["min_year"] = decade
        params["max_year"] = decade + 9

    if min_rating is not None:
        filters.append("cr.average_rating >= :min_rating")
        params["min_rating"] = min_rating

    where_clause = " AND ".join(filters)

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
            ct.poster_path,
            ct.overview
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY RANDOM()
        LIMIT 1
    """)

    row = db.execute(query_sql, params).fetchone()

    if not row:
        return None

    return RandomMovieResult(
        title_id=row[0],
        imdb_tconst=row[1],
        primary_title=row[2],
        start_year=row[3],
        runtime_minutes=row[4],
        genres=row[5],
        average_rating=row[6],
        num_votes=row[7],
        poster_path=row[8],
        overview=row[9],
    )


def _get_trending_row(
    db: Session,
    limit: int = 20,
    exclude_watched_profile_id: int | None = None,
) -> FeaturedRow | None:
    """Get the trending row using TMDB trending data."""
    from app.services.tmdb import get_trending_title_ids

    try:
        title_ids = get_trending_title_ids(db, limit=limit * 2)  # Fetch extra to account for watched exclusions
    except Exception as e:
        logger.warning(f"Failed to get trending from TMDB: {e}")
        title_ids = []

    if not title_ids:
        # Fallback to static popularity query
        return _get_row_by_query(
            db,
            "trending",
            "Trending Now",
            "COALESCE(cr.average_rating * LN(cr.num_votes + 1), 0) DESC",
            limit=limit,
            exclude_watched_profile_id=exclude_watched_profile_id,
        )

    # Build query with the specific title_ids in order (parameterized)
    params: dict = {"limit": limit}
    tid_placeholders = ", ".join(f":tid_{i}" for i in range(len(title_ids)))
    for i, tid in enumerate(title_ids):
        params[f"tid_{i}"] = tid
    filters = [f"ct.id IN ({tid_placeholders})"]

    if exclude_watched_profile_id is not None:
        filters.append(
            "ct.id NOT IN (SELECT title_id FROM watches WHERE profile_id = :exclude_profile_id)"
        )
        params["exclude_profile_id"] = exclude_watched_profile_id

    where_clause = " AND ".join(filters)

    # Build CASE statement to maintain TMDB trending order (parameterized)
    order_cases = " ".join(f"WHEN :tid_{i} THEN {i}" for i in range(len(title_ids)))
    order_clause = f"CASE ct.id {order_cases} END"

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
            ct.poster_path,
            cr.rt_critic_score
        FROM catalog_titles ct
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY {order_clause}
        LIMIT :limit
    """)

    rows = db.execute(query_sql, params).fetchall()

    if not rows:
        return None

    movies = [
        BrowseResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            poster_path=row[8],
            rt_critic_score=row[9],
        )
        for row in rows
    ]

    return FeaturedRow(id="trending", title="Trending Now", movies=movies)


def get_featured_rows(
    db: Session,
    limit: int = 20,
    exclude_watched_profile_id: int | None = None,
) -> list[FeaturedRow]:
    """Get multiple featured movie rows for the explore page."""
    rows = []

    # Trending Now - using TMDB trending data
    trending = _get_trending_row(
        db,
        limit=limit,
        exclude_watched_profile_id=exclude_watched_profile_id,
    )
    if trending:
        rows.append(trending)

    # New Releases - 2024+ sorted by popularity
    new_releases = _get_row_by_query(
        db,
        "new-releases",
        "New Releases",
        "COALESCE(cr.average_rating * LN(cr.num_votes + 1), 0) DESC",
        min_year=2024,
        limit=limit,
        exclude_watched_profile_id=exclude_watched_profile_id,
    )
    if new_releases:
        rows.append(new_releases)

    # Genre rows
    for genre in FEATURED_GENRES:
        genre_row = _get_row_by_query(
            db,
            genre.lower().replace("-", ""),
            f"{genre} Movies",
            "COALESCE(cr.average_rating * LN(cr.num_votes + 1), 0) DESC",
            genre_filter=genre,
            limit=limit,
            exclude_watched_profile_id=exclude_watched_profile_id,
        )
        if genre_row:
            rows.append(genre_row)

    return rows


def _get_row_by_query(
    db: Session,
    row_id: str,
    title: str,
    order_by: str,
    genre_filter: str | None = None,
    min_year: int | None = None,
    limit: int = 20,
    exclude_watched_profile_id: int | None = None,
) -> FeaturedRow | None:
    """Helper to get a featured row with a specific query."""
    filters = []
    params: dict = {"limit": limit}

    if genre_filter:
        filters.append("ct.genres ILIKE :row_genre")
        params["row_genre"] = f"%{genre_filter}%"
    if min_year is not None:
        filters.append("ct.start_year >= :row_min_year")
        params["row_min_year"] = min_year

    # Exclude watched movies if profile_id is provided
    if exclude_watched_profile_id is not None:
        filters.append(
            "ct.id NOT IN (SELECT title_id FROM watches WHERE profile_id = :exclude_profile_id)"
        )
        params["exclude_profile_id"] = exclude_watched_profile_id

    where_clause = " AND ".join(filters) if filters else "TRUE"

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
            ct.poster_path,
            cr.rt_critic_score
        FROM catalog_titles ct
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT :limit
    """)

    rows = db.execute(query_sql, params).fetchall()

    if not rows:
        return None

    movies = [
        BrowseResult(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            runtime_minutes=row[4],
            genres=row[5],
            average_rating=row[6],
            num_votes=row[7],
            poster_path=row[8],
            rt_critic_score=row[9],
        )
        for row in rows
    ]

    return FeaturedRow(id=row_id, title=title, movies=movies)


@dataclass
class LanguageOption:
    code: str
    count: int


def get_available_languages(db: Session) -> list[LanguageOption]:
    """Get available original languages from catalog_titles with at least 10 titles."""
    query_sql = text("""
        SELECT original_language, COUNT(*) AS cnt
        FROM catalog_titles
        WHERE original_language IS NOT NULL AND original_language != ''
        GROUP BY original_language
        HAVING COUNT(*) >= 10
        ORDER BY cnt DESC
    """)
    rows = db.execute(query_sql).fetchall()
    return [LanguageOption(code=row[0], count=row[1]) for row in rows]
