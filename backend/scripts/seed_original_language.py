"""Bulk-fetch original_language from TMDB for movies that have tmdb_id cached.

Usage:
    cd backend
    python -u -m scripts.seed_original_language [--limit 50000] [--batch-size 40]

For each movie that already has a tmdb_id but no original_language:
  1. Calls TMDB /find/{imdb_id} endpoint
  2. Extracts original_language from the response
  3. Updates catalog_titles.original_language

Rate limiting: TMDB allows ~40 requests per 10-second window.
"""
import argparse
import sys
import time

import httpx
from sqlalchemy import text

sys.path.insert(0, ".")
from app.config import settings
from app.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description="Seed original_language from TMDB")
    parser.add_argument("--limit", type=int, default=50000, help="Number of movies to process")
    parser.add_argument("--batch-size", type=int, default=40, help="Requests per rate-limit window")
    parser.add_argument("--window", type=int, default=10, help="Rate-limit window in seconds")
    args = parser.parse_args()

    if not settings.TMDB_API_KEY:
        print("Error: TMDB_API_KEY not set in .env")
        sys.exit(1)

    db = SessionLocal()

    # Get movies that need original_language — prioritize those with tmdb_id already cached
    print(f"Finding top {args.limit} movies without original_language...")
    rows = db.execute(text("""
        SELECT ct.id, ct.imdb_tconst
        FROM catalog_titles ct
        LEFT JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE ct.original_language IS NULL
        ORDER BY cr.num_votes DESC NULLS LAST
        LIMIT :limit
    """), {"limit": args.limit}).fetchall()

    total = len(rows)
    print(f"Found {total} movies to process")

    if total == 0:
        print("Nothing to do!")
        db.close()
        return

    api_calls = 0
    updated = 0
    batch_start = time.time()

    with httpx.Client() as client:
        for i, (title_id, imdb_tconst) in enumerate(rows):
            # Rate limiting
            if api_calls > 0 and api_calls % args.batch_size == 0:
                elapsed = time.time() - batch_start
                if elapsed < args.window:
                    sleep_time = args.window - elapsed
                    time.sleep(sleep_time)
                batch_start = time.time()

            try:
                resp = client.get(
                    f"https://api.themoviedb.org/3/find/{imdb_tconst}",
                    params={
                        "api_key": settings.TMDB_API_KEY,
                        "external_source": "imdb_id",
                    },
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  [{i+1}/{total}] {imdb_tconst} — API error: {e}")
                api_calls += 1
                continue

            api_calls += 1
            original_language = None

            for key in ("movie_results", "tv_results"):
                results = data.get(key, [])
                if results:
                    original_language = results[0].get("original_language")
                    break

            if original_language:
                db.execute(text("""
                    UPDATE catalog_titles
                    SET original_language = :lang
                    WHERE id = :title_id
                """), {"lang": original_language, "title_id": title_id})
                updated += 1

            # Commit and report every 100 movies
            if (i + 1) % 100 == 0:
                db.commit()
                print(
                    f"  [{i+1}/{total}] "
                    f"API calls: {api_calls} | "
                    f"Updated: {updated}"
                )

    # Final commit
    db.commit()
    db.close()

    print(f"\nDone!")
    print(f"  Movies processed: {total}")
    print(f"  API calls made: {api_calls}")
    print(f"  Movies with original_language set: {updated}")


if __name__ == "__main__":
    main()
