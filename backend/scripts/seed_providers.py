"""Bulk-fetch streaming provider data from TMDB for popular movies.

Usage:
    cd backend
    python -m scripts.seed_providers [--limit 10000] [--batch-size 40] [--region US]

Processes movies by popularity (num_votes DESC). For each movie:
  1. If no tmdb_id, looks it up via TMDB find-by-IMDB endpoint
  2. Fetches watch/providers for that tmdb_id
  3. Stores flatrate (streaming) providers in watch_providers table

Skips movies that already have cached provider data.
Respects TMDB rate limits (~40 requests per 10 seconds).
"""
import argparse
import sys
import time

import httpx
from sqlalchemy import text

sys.path.insert(0, ".")
from app.config import settings
from app.database import SessionLocal


def find_tmdb_id(client: httpx.Client, imdb_id: str) -> int | None:
    """Look up TMDB ID from an IMDB ID."""
    url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {"api_key": settings.TMDB_API_KEY, "external_source": "imdb_id"}
    try:
        resp = client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        for key in ("movie_results", "tv_results"):
            results = data.get(key, [])
            if results:
                return results[0].get("id")
    except Exception as e:
        print(f"  Error finding TMDB ID for {imdb_id}: {e}")
    return None


def fetch_providers(client: httpx.Client, tmdb_id: int, region: str) -> list[dict] | None:
    """Fetch streaming (flatrate) providers for a movie from TMDB."""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    params = {"api_key": settings.TMDB_API_KEY}
    try:
        resp = client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        region_data = data.get("results", {}).get(region)
        if not region_data:
            return []
        return region_data.get("flatrate", [])
    except Exception as e:
        print(f"  Error fetching providers for tmdb_id={tmdb_id}: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Seed streaming provider data for popular movies")
    parser.add_argument("--limit", type=int, default=10000, help="Number of movies to process")
    parser.add_argument("--batch-size", type=int, default=38, help="Requests per rate-limit window")
    parser.add_argument("--region", type=str, default="US", help="Region for provider data")
    args = parser.parse_args()

    if not settings.TMDB_API_KEY:
        print("Error: TMDB_API_KEY not set")
        sys.exit(1)

    db = SessionLocal()

    # Get popular movies ordered by votes, skipping those already cached
    print(f"Finding top {args.limit} popular movies without cached provider data...")
    rows = db.execute(text("""
        SELECT ct.id, ct.imdb_tconst, ct.tmdb_id
        FROM catalog_titles ct
        JOIN catalog_ratings cr ON cr.title_id = ct.id
        WHERE ct.id NOT IN (
            SELECT DISTINCT title_id FROM watch_providers WHERE region = :region
        )
        ORDER BY cr.num_votes DESC
        LIMIT :limit
    """), {"limit": args.limit, "region": args.region}).fetchall()

    total = len(rows)
    print(f"Found {total} movies to process")

    if total == 0:
        print("Nothing to do!")
        db.close()
        return

    api_calls = 0
    movies_with_providers = 0
    total_providers_added = 0
    batch_start = time.time()

    with httpx.Client() as client:
        for i, (title_id, imdb_tconst, tmdb_id) in enumerate(rows):
            # Rate limiting: pause after each batch
            if api_calls > 0 and api_calls % args.batch_size == 0:
                elapsed = time.time() - batch_start
                if elapsed < 10.0:
                    sleep_time = 10.0 - elapsed
                    time.sleep(sleep_time)
                batch_start = time.time()

            # Step 1: Get tmdb_id if we don't have one
            if not tmdb_id:
                tmdb_id = find_tmdb_id(client, imdb_tconst)
                api_calls += 1
                if tmdb_id:
                    db.execute(
                        text("UPDATE catalog_titles SET tmdb_id = :tmdb_id WHERE id = :id"),
                        {"tmdb_id": tmdb_id, "id": title_id},
                    )

            if not tmdb_id:
                if (i + 1) % 100 == 0:
                    print(f"  [{i+1}/{total}] {imdb_tconst} — no TMDB match, skipping")
                continue

            # Step 2: Fetch streaming providers
            providers = fetch_providers(client, tmdb_id, args.region)
            api_calls += 1

            if providers is None:
                continue

            # Step 3: Store in DB
            if providers:
                movies_with_providers += 1
                for p in providers:
                    db.execute(text("""
                        INSERT INTO watch_providers
                            (title_id, provider_id, provider_name, logo_path, provider_type, region, display_priority)
                        VALUES
                            (:title_id, :provider_id, :provider_name, :logo_path, 'flatrate', :region, :display_priority)
                        ON CONFLICT (title_id, provider_id, provider_type, region) DO NOTHING
                    """), {
                        "title_id": title_id,
                        "provider_id": p["provider_id"],
                        "provider_name": p["provider_name"],
                        "logo_path": p.get("logo_path"),
                        "region": args.region,
                        "display_priority": p.get("display_priority"),
                    })
                    total_providers_added += 1

            # Commit every 50 movies
            if (i + 1) % 50 == 0:
                db.commit()
                print(
                    f"  [{i+1}/{total}] "
                    f"API calls: {api_calls} | "
                    f"Movies with streaming: {movies_with_providers} | "
                    f"Provider entries: {total_providers_added}"
                )

    # Final commit
    db.commit()
    db.close()

    print(f"\nDone!")
    print(f"  Movies processed: {total}")
    print(f"  API calls made: {api_calls}")
    print(f"  Movies with streaming providers: {movies_with_providers}")
    print(f"  Provider entries added: {total_providers_added}")


if __name__ == "__main__":
    main()
