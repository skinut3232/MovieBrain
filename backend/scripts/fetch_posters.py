"""Bulk-fetch poster_paths from TMDb for top movies by vote count.

Usage:
    cd backend
    python -m scripts.fetch_posters [--limit 10000] [--batch-size 40]

Respects TMDb rate limits (~40 requests/second).
"""
import argparse
import sys
import time

import httpx
from sqlalchemy import text

sys.path.insert(0, ".")
from app.config import settings
from app.database import SessionLocal


def fetch_poster(client: httpx.Client, imdb_id: str) -> str | None:
    url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {"api_key": settings.TMDB_API_KEY, "external_source": "imdb_id"}
    try:
        resp = client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        for key in ("movie_results", "tv_results"):
            results = data.get(key, [])
            if results and results[0].get("poster_path"):
                return results[0]["poster_path"]
    except Exception as e:
        print(f"  Error fetching {imdb_id}: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch TMDb posters for top movies")
    parser.add_argument("--limit", type=int, default=10000, help="Number of movies to process")
    parser.add_argument("--batch-size", type=int, default=40, help="Requests per second batch")
    args = parser.parse_args()

    if not settings.TMDB_API_KEY:
        print("ERROR: TMDB_API_KEY not set in .env")
        sys.exit(1)

    db = SessionLocal()
    client = httpx.Client()

    # Get top movies by num_votes that don't have a poster_path yet
    rows = db.execute(
        text("""
            SELECT ct.id, ct.imdb_tconst
            FROM catalog_titles ct
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE ct.poster_path IS NULL
              AND ct.title_type = 'movie'
            ORDER BY cr.num_votes DESC NULLS LAST
            LIMIT :limit
        """),
        {"limit": args.limit},
    ).fetchall()

    print(f"Found {len(rows)} movies without posters (limit={args.limit})")

    fetched = 0
    failed = 0

    for i, (title_id, imdb_tconst) in enumerate(rows):
        poster_path = fetch_poster(client, imdb_tconst)

        if poster_path:
            db.execute(
                text("UPDATE catalog_titles SET poster_path = :path WHERE id = :id"),
                {"path": poster_path, "id": title_id},
            )
            fetched += 1
        else:
            failed += 1

        # Commit every 100 rows
        if (i + 1) % 100 == 0:
            db.commit()
            print(f"  Progress: {i + 1}/{len(rows)} (fetched={fetched}, failed={failed})")

        # Rate limiting: pause after each batch
        if (i + 1) % args.batch_size == 0:
            time.sleep(1.0)

    db.commit()
    client.close()
    db.close()

    print(f"\nDone! Fetched: {fetched}, Failed/No poster: {failed}, Total processed: {len(rows)}")


if __name__ == "__main__":
    main()
