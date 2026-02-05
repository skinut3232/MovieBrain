"""Generate movie embeddings using OpenAI text-embedding-3-small.

Queries movies that have ratings (indicating they are popular enough to recommend),
joins crew/principals for director and cast names, builds embedding text,
and batch-calls OpenAI to generate embeddings. Upserts into movie_embeddings.

Usage:
    cd backend
    python -m scripts.generate_embeddings
"""

import sys
import time

import numpy as np
from openai import OpenAI
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal

BATCH_SIZE = 500
MODEL_ID = settings.EMBEDDING_MODEL
DIMENSIONS = settings.EMBEDDING_DIMENSIONS


def count_movies_needing_embeddings(db) -> int:
    """Count movies with ratings that don't yet have embeddings."""
    query = text("""
        SELECT COUNT(*)
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        LEFT JOIN movie_embeddings me ON me.title_id = ct.id AND me.model_id = :model_id
        WHERE me.title_id IS NULL
    """)
    return db.execute(query, {"model_id": MODEL_ID}).scalar()


def get_movies_needing_embeddings(db, limit: int = 500) -> list[dict]:
    """Get a batch of movies with ratings that don't yet have embeddings."""
    query = text("""
        SELECT
            ct.id AS title_id,
            ct.primary_title,
            ct.start_year,
            ct.genres,
            ARRAY(
                SELECT cp.primary_name
                FROM catalog_crew cc2
                CROSS JOIN LATERAL unnest(cc2.director_nconsts) AS d(nconst)
                JOIN catalog_people cp ON cp.imdb_nconst = d.nconst
                WHERE cc2.title_id = ct.id
                LIMIT 3
            ) AS directors,
            ARRAY(
                SELECT cp.primary_name
                FROM catalog_principals cprin
                JOIN catalog_people cp ON cp.id = cprin.person_id
                WHERE cprin.title_id = ct.id
                  AND cprin.category IN ('actor', 'actress')
                ORDER BY cprin.ordering
                LIMIT 5
            ) AS cast_members
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        LEFT JOIN movie_embeddings me ON me.title_id = ct.id AND me.model_id = :model_id
        WHERE me.title_id IS NULL
        ORDER BY cr.num_votes DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"model_id": MODEL_ID, "limit": limit})
    return [dict(row._mapping) for row in result]


def build_embedding_text(movie: dict) -> str:
    """Build embedding text from movie data."""
    parts = []
    title = movie["primary_title"]
    year = movie["start_year"]

    if year:
        parts.append(f"{title} ({year})")
    else:
        parts.append(title)

    if movie["genres"]:
        parts.append(movie["genres"])

    directors = movie.get("directors") or []
    if directors:
        parts.append(f"Directed by {', '.join(directors)}")

    cast_members = movie.get("cast_members") or []
    if cast_members:
        parts.append(f"Starring {', '.join(cast_members)}")

    return ". ".join(parts) + "."


def generate_embeddings_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Call OpenAI embeddings API for a batch of texts."""
    response = client.embeddings.create(
        model=MODEL_ID,
        input=texts,
        dimensions=DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def upsert_embeddings(db, rows: list[tuple[int, str, list[float]]]):
    """Upsert embeddings into movie_embeddings table."""
    for title_id, emb_text, embedding in rows:
        vec_str = "[" + ",".join(str(x) for x in embedding) + "]"
        db.execute(
            text("""
                INSERT INTO movie_embeddings (title_id, model_id, embedding, embedding_text, updated_at)
                VALUES (:title_id, :model_id, :embedding, :embedding_text, now())
                ON CONFLICT (title_id, model_id)
                DO UPDATE SET embedding = :embedding, embedding_text = :embedding_text, updated_at = now()
            """),
            {
                "title_id": title_id,
                "model_id": MODEL_ID,
                "embedding": vec_str,
                "embedding_text": emb_text,
            },
        )
    db.commit()


def main():
    if not settings.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set in .env")
        sys.exit(1)

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    db = SessionLocal()

    try:
        print(f"Model: {MODEL_ID}, Dimensions: {DIMENSIONS}")
        print("Counting movies needing embeddings...")

        total = count_movies_needing_embeddings(db)
        print(f"Found {total} movies needing embeddings")

        if total == 0:
            print("All movies already have embeddings.")
            return

        processed = 0
        while True:
            movies = get_movies_needing_embeddings(db, limit=BATCH_SIZE)
            if not movies:
                break

            texts = [build_embedding_text(m) for m in movies]

            retries = 0
            while retries < 3:
                try:
                    embeddings = generate_embeddings_batch(client, texts)
                    break
                except Exception as e:
                    retries += 1
                    if retries >= 3:
                        print(f"  ERROR: Failed after 3 retries: {e}")
                        raise
                    wait_time = 2 ** retries
                    print(f"  Retry {retries}/3 after error: {e} (waiting {wait_time}s)")
                    time.sleep(wait_time)

            rows = [
                (movies[j]["title_id"], texts[j], embeddings[j])
                for j in range(len(movies))
            ]
            upsert_embeddings(db, rows)
            processed += len(movies)
            print(f"  Progress: {processed}/{total} ({processed * 100 // total}%)")

            # Rate limiting: brief pause between batches
            time.sleep(0.5)

        print(f"Done! Generated embeddings for {processed} movies.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
