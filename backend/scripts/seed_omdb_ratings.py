"""Bulk-fetch RT and Metacritic scores from OMDb for popular movies.

Usage:
    cd backend
    python -u -m scripts.seed_omdb_ratings [--limit 10000] [--batch-size 900] [--window 86400]

Processes movies by popularity (num_votes DESC). For each movie:
  1. Calls OMDb API with the IMDB tconst
  2. Parses Rotten Tomatoes and Metacritic scores from the response
  3. Stores scores in catalog_ratings

Skips movies that already have fresh omdb_fetched_at data.

Rate limiting defaults: free tier allows ~1000 requests/day, so default
batch-size=900 with window=86400 (24h). For paid keys, use smaller windows
(e.g. --batch-size 100 --window 10).
"""
import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import text

sys.path.insert(0, ".")
from app.config import settings
from app.database import SessionLocal
from app.services.omdb import parse_metacritic, parse_rt_percentage


def main():
    parser = argparse.ArgumentParser(description="Seed RT/Metacritic scores from OMDb")
    parser.add_argument("--limit", type=int, default=10000, help="Number of movies to process")
    parser.add_argument("--batch-size", type=int, default=900, help="Requests per rate-limit window")
    parser.add_argument("--window", type=int, default=86400, help="Rate-limit window in seconds (default: 24h for free tier)")
    args = parser.parse_args()

    if not settings.OMDB_API_KEY:
        print("Error: OMDB_API_KEY not set in .env")
        sys.exit(1)

    db = SessionLocal()
    cache_days = 90

    cutoff = datetime.now(timezone.utc) - timedelta(days=cache_days)
    cutoff_str = cutoff.isoformat()

    # Get popular movies that need OMDb data
    print(f"Finding top {args.limit} popular movies without fresh OMDb data...")
    rows = db.execute(text("""
        SELECT ct.id, ct.imdb_tconst, cr.id as rating_id
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE cr.omdb_fetched_at IS NULL
           OR cr.omdb_fetched_at < :cutoff
        ORDER BY cr.num_votes DESC
        LIMIT :limit
    """), {"limit": args.limit, "cutoff": cutoff_str}).fetchall()

    total = len(rows)
    print(f"Found {total} movies to process")

    if total == 0:
        print("Nothing to do!")
        db.close()
        return

    api_calls = 0
    movies_with_rt = 0
    movies_with_mc = 0
    batch_start = time.time()

    with httpx.Client() as client:
        for i, (title_id, imdb_tconst, rating_id) in enumerate(rows):
            # Rate limiting
            if api_calls > 0 and api_calls % args.batch_size == 0:
                elapsed = time.time() - batch_start
                if elapsed < args.window:
                    sleep_time = args.window - elapsed
                    print(f"\n  Rate limit reached ({args.batch_size} calls). Sleeping {sleep_time:.0f}s...")
                    time.sleep(sleep_time)
                batch_start = time.time()

            # Call OMDb
            try:
                resp = client.get(
                    "https://www.omdbapi.com/",
                    params={"apikey": settings.OMDB_API_KEY, "i": imdb_tconst},
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  [{i+1}/{total}] {imdb_tconst} — API error: {e}")
                api_calls += 1
                continue

            api_calls += 1

            rt_critic_score = None
            metacritic_score = None

            if data.get("Response") != "False":
                for rating in data.get("Ratings", []):
                    source = rating.get("Source", "")
                    value = rating.get("Value", "")
                    if source == "Rotten Tomatoes":
                        rt_critic_score = parse_rt_percentage(value)
                    elif source == "Metacritic":
                        metacritic_score = parse_metacritic(value)

                if metacritic_score is None:
                    metacritic_score = parse_metacritic(data.get("Metascore"))

            if rt_critic_score is not None:
                movies_with_rt += 1
            if metacritic_score is not None:
                movies_with_mc += 1

            # Update DB
            db.execute(text("""
                UPDATE catalog_ratings
                SET rt_critic_score = :rt,
                    metacritic_score = :mc,
                    omdb_fetched_at = :now
                WHERE id = :rating_id
            """), {
                "rt": rt_critic_score,
                "mc": metacritic_score,
                "now": datetime.now(timezone.utc).isoformat(),
                "rating_id": rating_id,
            })

            # Commit and report every 50 movies
            if (i + 1) % 50 == 0:
                db.commit()
                print(
                    f"  [{i+1}/{total}] "
                    f"API calls: {api_calls} | "
                    f"With RT: {movies_with_rt} | "
                    f"With Metacritic: {movies_with_mc}"
                )

    # Final commit
    db.commit()
    db.close()

    print(f"\nDone!")
    print(f"  Movies processed: {total}")
    print(f"  API calls made: {api_calls}")
    print(f"  Movies with RT score: {movies_with_rt}")
    print(f"  Movies with Metacritic score: {movies_with_mc}")


if __name__ == "__main__":
    main()
