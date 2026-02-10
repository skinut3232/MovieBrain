from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.collection import Collection, CollectionItem


@dataclass
class CollectionTitle:
    title_id: int
    imdb_tconst: str
    primary_title: str
    start_year: int | None
    genres: str | None
    average_rating: float | None
    num_votes: int | None
    poster_path: str | None
    position: int | None = None
    rt_critic_score: int | None = None


def get_all_collections(db: Session) -> list[Collection]:
    """Get all collections ordered by name."""
    return db.query(Collection).order_by(Collection.name).all()


def get_collection_by_id(db: Session, collection_id: int) -> Collection | None:
    """Get a single collection by ID."""
    return db.query(Collection).filter(Collection.id == collection_id).first()


def get_collection_movies(
    db: Session,
    collection: Collection,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[CollectionTitle], int]:
    """Get movies for a collection (curated or auto-generated)."""
    offset = (page - 1) * limit

    if collection.collection_type == "curated":
        return _get_curated_collection_movies(db, collection.id, page, limit)
    else:
        return _get_auto_collection_movies(db, collection.query_params or {}, page, limit)


def _get_curated_collection_movies(
    db: Session,
    collection_id: int,
    page: int,
    limit: int,
) -> tuple[list[CollectionTitle], int]:
    """Get movies from a curated collection using collection_items table."""
    offset = (page - 1) * limit

    # Get total count
    total = db.query(CollectionItem).filter(
        CollectionItem.collection_id == collection_id
    ).count()

    # Get items with movie details
    query_sql = text("""
        SELECT
            ct.id AS title_id,
            ct.imdb_tconst,
            ct.primary_title,
            ct.start_year,
            ct.genres,
            cr.average_rating,
            cr.num_votes,
            ct.poster_path,
            ci.position,
            cr.rt_critic_score
        FROM collection_items ci
        JOIN catalog_titles ct ON ct.id = ci.title_id
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE ci.collection_id = :collection_id
        ORDER BY ci.position ASC
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(
        query_sql,
        {"collection_id": collection_id, "limit": limit, "offset": offset}
    ).fetchall()

    return [
        CollectionTitle(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            genres=row[4],
            average_rating=row[5],
            num_votes=row[6],
            poster_path=row[7],
            position=row[8],
            rt_critic_score=row[9],
        )
        for row in rows
    ], total


def _get_auto_collection_movies(
    db: Session,
    query_params: dict[str, Any],
    page: int,
    limit: int,
) -> tuple[list[CollectionTitle], int]:
    """Get movies for an auto-generated collection based on query_params."""
    offset = (page - 1) * limit

    filters = []
    params: dict = {"limit": limit, "offset": offset}

    # Parse query_params for filtering
    if genre := query_params.get("genre"):
        filters.append("ct.genres ILIKE :genre")
        params["genre"] = f"%{genre}%"

    if (min_year := query_params.get("min_year")) is not None:
        filters.append("ct.start_year >= :min_year")
        params["min_year"] = min_year

    if (max_year := query_params.get("max_year")) is not None:
        filters.append("ct.start_year <= :max_year")
        params["max_year"] = max_year

    if (min_rating := query_params.get("min_rating")) is not None:
        filters.append("cr.average_rating >= :min_rating")
        params["min_rating"] = min_rating

    if (min_votes := query_params.get("min_votes")) is not None:
        filters.append("cr.num_votes >= :min_votes")
        params["min_votes"] = min_votes

    where_clause = " AND ".join(filters) if filters else "TRUE"

    # Determine sort order
    sort_by = query_params.get("sort_by", "popularity")
    sort_clauses = {
        "popularity": "cr.average_rating * LN(cr.num_votes + 1) DESC",
        "rating": "cr.average_rating DESC NULLS LAST",
        "year_desc": "ct.start_year DESC NULLS LAST",
        "votes": "cr.num_votes DESC NULLS LAST",
    }
    order_by = sort_clauses.get(sort_by, sort_clauses["popularity"])

    # Get total count
    count_sql = text(f"""
        SELECT COUNT(*)
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
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
            ct.genres,
            cr.average_rating,
            cr.num_votes,
            ct.poster_path,
            cr.rt_critic_score
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(query_sql, params).fetchall()

    return [
        CollectionTitle(
            title_id=row[0],
            imdb_tconst=row[1],
            primary_title=row[2],
            start_year=row[3],
            genres=row[4],
            average_rating=row[5],
            num_votes=row[6],
            poster_path=row[7],
            rt_critic_score=row[8],
        )
        for row in rows
    ], total


def seed_default_collections(db: Session) -> None:
    """Create default auto-generated collections if they don't exist."""
    default_collections = [
        {
            "name": "Top Rated 80s",
            "description": "The highest-rated movies from the 1980s",
            "collection_type": "auto",
            "query_params": {
                "min_year": 1980,
                "max_year": 1989,
                "min_votes": 10000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Top Rated 90s",
            "description": "The highest-rated movies from the 1990s",
            "collection_type": "auto",
            "query_params": {
                "min_year": 1990,
                "max_year": 1999,
                "min_votes": 10000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Best Horror",
            "description": "Top-rated horror movies of all time",
            "collection_type": "auto",
            "query_params": {
                "genre": "Horror",
                "min_votes": 50000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Best Sci-Fi",
            "description": "Top-rated science fiction movies",
            "collection_type": "auto",
            "query_params": {
                "genre": "Sci-Fi",
                "min_votes": 50000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Best Comedies",
            "description": "Highest-rated comedy movies",
            "collection_type": "auto",
            "query_params": {
                "genre": "Comedy",
                "min_votes": 100000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Classic Thrillers",
            "description": "Must-watch thriller movies",
            "collection_type": "auto",
            "query_params": {
                "genre": "Thriller",
                "min_votes": 75000,
                "sort_by": "rating",
            },
        },
        {
            "name": "Epic Dramas",
            "description": "Critically acclaimed drama films",
            "collection_type": "auto",
            "query_params": {
                "genre": "Drama",
                "min_rating": 8.0,
                "min_votes": 100000,
                "sort_by": "popularity",
            },
        },
        {
            "name": "Modern Classics (2010s)",
            "description": "The best movies of the 2010s",
            "collection_type": "auto",
            "query_params": {
                "min_year": 2010,
                "max_year": 2019,
                "min_rating": 7.5,
                "min_votes": 200000,
                "sort_by": "rating",
            },
        },
    ]

    for coll_data in default_collections:
        existing = db.query(Collection).filter(Collection.name == coll_data["name"]).first()
        if not existing:
            collection = Collection(
                name=coll_data["name"],
                description=coll_data["description"],
                collection_type=coll_data["collection_type"],
                query_params=coll_data["query_params"],
            )
            db.add(collection)

    db.commit()
