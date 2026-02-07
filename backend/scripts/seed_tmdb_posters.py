"""Bulk-fetch poster, overview, and trailer from TMDB for popular movies.

Usage:
    cd backend
    python -u -m scripts.seed_tmdb_posters [--limit 2000] [--delay 0.25]

Processes movies by popularity (num_votes DESC) that are missing poster_path.
TMDB free tier allows ~40 requests/10 seconds, so default delay is 0.25s.
"""
import argparse
import sys
import time

sys.path.insert(0, ".")
from app.config import settings
from app.database import SessionLocal
from app.services.tmdb import fetch_movie_details_from_tmdb

from sqlalchemy import text


def main():
    parser = argparse.ArgumentParser(description="Seed TMDB posters for popular movies")
    parser.add_argument("--limit", type=int, default=2000, help="Number of movies to process")
    parser.add_argument("--delay", type=float, default=0.25, help="Delay between API calls in seconds")
    args = parser.parse_args()

    if not settings.TMDB_API_KEY:
        print("Error: TMDB_API_KEY not set in .env")
        sys.exit(1)

    db = SessionLocal()

    print(f"Finding top {args.limit} popular movies without TMDB poster...")
    rows = db.execute(text("""
        SELECT ct.id, ct.imdb_tconst
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE ct.poster_path IS NULL
        ORDER BY cr.num_votes DESC
        LIMIT :limit
    """), {"limit": args.limit}).fetchall()

    total = len(rows)
    print(f"Found {total} movies to process")

    if total == 0:
        print("Nothing to do!")
        db.close()
        return

    fetched = 0
    errors = 0

    for i, (title_id, imdb_tconst) in enumerate(rows):
        try:
            details = fetch_movie_details_from_tmdb(imdb_tconst)
        except Exception as e:
            print(f"  [{i+1}/{total}] {imdb_tconst} — error: {e}")
            errors += 1
            time.sleep(args.delay)
            continue

        if details and details.get("poster_path"):
            db.execute(text("""
                UPDATE catalog_titles
                SET tmdb_id = COALESCE(tmdb_id, :tmdb_id),
                    poster_path = COALESCE(poster_path, :poster_path),
                    overview = COALESCE(overview, :overview),
                    trailer_key = COALESCE(trailer_key, :trailer_key)
                WHERE id = :title_id
            """), {
                "tmdb_id": details.get("tmdb_id"),
                "poster_path": details.get("poster_path"),
                "overview": details.get("overview"),
                "trailer_key": details.get("trailer_key"),
                "title_id": title_id,
            })
            fetched += 1
        else:
            errors += 1

        if (i + 1) % 50 == 0:
            db.commit()
            print(f"  [{i+1}/{total}] Fetched: {fetched} | Errors: {errors}")

        time.sleep(args.delay)

    db.commit()
    db.close()

    print(f"\nDone!")
    print(f"  Movies processed: {total}")
    print(f"  Posters fetched: {fetched}")
    print(f"  Errors/missing: {errors}")


if __name__ == "__main__":
    main()
