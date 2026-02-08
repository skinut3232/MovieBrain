import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.config import settings
from app.models.catalog import CatalogTitle, ProviderMaster, TrendingCache, WatchProvider


def get_poster_url(poster_path: str | None) -> str | None:
    """Build full poster URL from a poster_path, or return None."""
    if not poster_path:
        return None
    return f"{settings.TMDB_IMAGE_BASE_URL}w300{poster_path}"


def fetch_poster_path_from_tmdb(imdb_id: str) -> str | None:
    """Fetch poster_path from TMDb API using an IMDb ID.

    Uses the "find by external ID" endpoint.
    Returns the poster_path string (e.g. "/abc123.jpg") or None.
    """
    if not settings.TMDB_API_KEY:
        return None

    url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "external_source": "imdb_id",
    }

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

        # Check movie_results first, then tv_results
        for key in ("movie_results", "tv_results"):
            results = data.get(key, [])
            if results and results[0].get("poster_path"):
                return results[0]["poster_path"]
    except (httpx.HTTPError, KeyError, IndexError) as e:
        logger.warning("Failed to fetch poster from TMDB for %s: %s", imdb_id, e)

    return None


def fetch_movie_details_from_tmdb(imdb_id: str) -> dict | None:
    """Fetch full movie details from TMDb API using an IMDb ID.

    Uses the "find by external ID" endpoint to get TMDb ID,
    then fetches movie details with videos appended.
    Returns dict with tmdb_id, poster_path, overview, trailer_key (or None for each).
    """
    if not settings.TMDB_API_KEY:
        return None

    # First find the movie by IMDb ID
    find_url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "external_source": "imdb_id",
    }

    try:
        resp = httpx.get(find_url, params=params, timeout=10.0)
        resp.raise_for_status()
        find_data = resp.json()

        tmdb_id = None
        media_type = None
        result = {"tmdb_id": None, "poster_path": None, "overview": None, "trailer_key": None}

        # Check movie_results first, then tv_results
        for key, mtype in [("movie_results", "movie"), ("tv_results", "tv")]:
            results = find_data.get(key, [])
            if results:
                item = results[0]
                tmdb_id = item.get("id")
                media_type = mtype
                result["tmdb_id"] = tmdb_id
                result["poster_path"] = item.get("poster_path")
                result["overview"] = item.get("overview")
                break

        if not tmdb_id:
            return result

        # Fetch videos to get trailer
        videos_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos"
        videos_resp = httpx.get(videos_url, params={"api_key": settings.TMDB_API_KEY}, timeout=10.0)
        videos_resp.raise_for_status()
        videos_data = videos_resp.json()

        # Find YouTube trailer (prefer official trailers)
        videos = videos_data.get("results", [])
        trailer_key = None

        # Priority: Official Trailer > Trailer > Teaser > any YouTube video
        for video_type in ["Trailer", "Teaser"]:
            for video in videos:
                if (
                    video.get("site") == "YouTube"
                    and video.get("type") == video_type
                    and video.get("official", True)
                ):
                    trailer_key = video.get("key")
                    break
            if trailer_key:
                break

        # Fallback to any YouTube video if no official trailer
        if not trailer_key:
            for video in videos:
                if video.get("site") == "YouTube":
                    trailer_key = video.get("key")
                    break

        result["trailer_key"] = trailer_key
        return result

    except (httpx.HTTPError, KeyError, IndexError) as e:
        logger.warning("Failed to fetch movie details from TMDB for %s: %s", imdb_id, e)

    return None


def get_or_fetch_poster_path(db: Session, title: CatalogTitle) -> str | None:
    """Return cached poster_path, or fetch from TMDb and cache it.

    This is the lazy-fill mechanism: if poster_path is null when a movie
    is requested, we attempt to fetch it from TMDb and store it.
    """
    if title.poster_path is not None:
        return title.poster_path

    poster_path = fetch_poster_path_from_tmdb(title.imdb_tconst)
    if poster_path:
        title.poster_path = poster_path
        db.commit()

    return poster_path


def get_or_fetch_movie_details(db: Session, title: CatalogTitle) -> dict:
    """Return cached movie details, or fetch from TMDb and cache them.

    Fetches poster_path, overview, trailer_key, and tmdb_id if not already cached.
    Returns dict with poster_path, overview, trailer_key.
    """
    needs_fetch = (
        title.poster_path is None
        or title.overview is None
        or title.trailer_key is None
        or title.tmdb_id is None
    )

    if not needs_fetch:
        return {
            "poster_path": title.poster_path,
            "overview": title.overview,
            "trailer_key": title.trailer_key,
        }

    details = fetch_movie_details_from_tmdb(title.imdb_tconst)
    if details:
        # Only update fields that are currently null
        if title.tmdb_id is None and details.get("tmdb_id"):
            title.tmdb_id = details["tmdb_id"]
        if title.poster_path is None and details.get("poster_path"):
            title.poster_path = details["poster_path"]
        if title.overview is None and details.get("overview"):
            title.overview = details["overview"]
        if title.trailer_key is None and details.get("trailer_key"):
            title.trailer_key = details["trailer_key"]
        db.commit()

    return {
        "poster_path": title.poster_path,
        "overview": title.overview,
        "trailer_key": title.trailer_key,
    }


# Trending cache settings
TRENDING_CACHE_DAYS = 7


def fetch_tmdb_trending() -> list[dict]:
    """Fetch trending movies from TMDB API.

    Returns list of dicts with id, title, release_date, imdb_id (if available).
    """
    if not settings.TMDB_API_KEY:
        return []

    url = "https://api.themoviedb.org/3/trending/movie/week"
    params = {"api_key": settings.TMDB_API_KEY}

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except (httpx.HTTPError, KeyError) as e:
        logger.warning("Failed to fetch trending from TMDB: %s", e)
        return []


def get_imdb_id_from_tmdb(tmdb_id: int) -> str | None:
    """Get IMDB ID for a TMDB movie ID."""
    if not settings.TMDB_API_KEY:
        return None

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids"
    params = {"api_key": settings.TMDB_API_KEY}

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return data.get("imdb_id")
    except (httpx.HTTPError, KeyError) as e:
        logger.warning("Failed to get IMDB ID from TMDB for tmdb_id %s: %s", tmdb_id, e)
        return None


def refresh_trending_cache(db: Session) -> int:
    """Refresh the trending cache from TMDB.

    Returns the number of movies successfully matched to catalog.
    """
    trending = fetch_tmdb_trending()
    if not trending:
        return 0

    # Build new entries first before deleting old ones
    new_entries = []
    matched_count = 0

    for rank, movie in enumerate(trending, start=1):
        tmdb_id = movie.get("id")
        if not tmdb_id:
            continue

        # Try to find by tmdb_id first
        title = db.query(CatalogTitle).filter(CatalogTitle.tmdb_id == tmdb_id).first()

        # Fallback: get IMDB ID from TMDB and match by imdb_tconst
        if not title:
            imdb_id = get_imdb_id_from_tmdb(tmdb_id)
            if imdb_id:
                title = db.query(CatalogTitle).filter(
                    CatalogTitle.imdb_tconst == imdb_id
                ).first()
                # If found, update the tmdb_id for future lookups
                if title and not title.tmdb_id:
                    title.tmdb_id = tmdb_id

        new_entries.append(TrendingCache(
            tmdb_id=tmdb_id,
            title_id=title.id if title else None,
            rank=rank,
        ))

        if title:
            matched_count += 1

    # Only delete old entries after successfully building new ones
    db.query(TrendingCache).delete()
    for entry in new_entries:
        db.add(entry)

    db.commit()
    return matched_count


def is_trending_cache_fresh(db: Session) -> bool:
    """Check if the trending cache is fresh (less than TRENDING_CACHE_DAYS old)."""
    latest = db.query(TrendingCache).order_by(TrendingCache.fetched_at.desc()).first()
    if not latest:
        return False

    cutoff = datetime.now(timezone.utc) - timedelta(days=TRENDING_CACHE_DAYS)
    return latest.fetched_at > cutoff


def get_trending_title_ids(db: Session, limit: int = 20) -> list[int]:
    """Get cached trending movie title IDs, refreshing if stale.

    Returns list of title_ids in trending order.
    """
    # Check if cache is fresh, refresh if not
    if not is_trending_cache_fresh(db):
        refresh_trending_cache(db)

    # Get cached results with matched titles
    results = (
        db.query(TrendingCache.title_id)
        .filter(TrendingCache.title_id.isnot(None))
        .order_by(TrendingCache.rank)
        .limit(limit)
        .all()
    )

    return [r[0] for r in results]


# Watch Provider functions
PROVIDER_CACHE_DAYS = 30


def fetch_watch_providers_from_tmdb(tmdb_id: int, region: str = "US") -> dict | None:
    """Fetch watch providers for a movie from TMDB API.

    Returns dict with flatrate, rent, buy lists of provider dicts.
    """
    if not settings.TMDB_API_KEY:
        return None

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    params = {"api_key": settings.TMDB_API_KEY}

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", {}).get(region)
    except (httpx.HTTPError, KeyError) as e:
        logger.warning("Failed to fetch watch providers from TMDB for tmdb_id %s: %s", tmdb_id, e)
        return None


def get_or_fetch_watch_providers(
    db: Session, title: CatalogTitle, region: str = "US"
) -> list[WatchProvider]:
    """Return cached watch providers, or fetch from TMDB and cache them."""
    # Check for cached providers that are still fresh
    cutoff = datetime.now(timezone.utc) - timedelta(days=PROVIDER_CACHE_DAYS)
    cached = (
        db.query(WatchProvider)
        .filter(
            WatchProvider.title_id == title.id,
            WatchProvider.region == region,
            WatchProvider.fetched_at > cutoff,
        )
        .all()
    )

    if cached:
        return cached

    # Need TMDB ID to fetch providers
    if not title.tmdb_id:
        # Try to get tmdb_id first via movie details fetch
        details = get_or_fetch_movie_details(db, title)
        if not title.tmdb_id:
            return []

    provider_data = fetch_watch_providers_from_tmdb(title.tmdb_id, region)
    if not provider_data:
        return []

    # Delete stale entries only after successful fetch
    db.query(WatchProvider).filter(
        WatchProvider.title_id == title.id,
        WatchProvider.region == region,
    ).delete()

    providers = []
    for ptype in ("flatrate", "rent", "buy"):
        for p in provider_data.get(ptype, []):
            wp = WatchProvider(
                title_id=title.id,
                provider_id=p["provider_id"],
                provider_name=p["provider_name"],
                logo_path=p.get("logo_path"),
                provider_type=ptype,
                region=region,
                display_priority=p.get("display_priority"),
            )
            db.add(wp)
            providers.append(wp)

    db.commit()
    return providers


def refresh_provider_master(db: Session, region: str = "US") -> int:
    """Fetch full provider list from TMDB and seed/update provider_master table.

    Returns number of providers updated.
    """
    if not settings.TMDB_API_KEY:
        return 0

    url = "https://api.themoviedb.org/3/watch/providers/movie"
    params = {"api_key": settings.TMDB_API_KEY, "watch_region": region}

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, KeyError) as e:
        logger.warning("Failed to fetch provider master list from TMDB: %s", e)
        return 0

    results = data.get("results", [])
    count = 0

    for p in results:
        pid = p.get("provider_id")
        if not pid:
            continue

        existing = db.query(ProviderMaster).filter(ProviderMaster.provider_id == pid).first()
        if existing:
            existing.provider_name = p.get("provider_name", existing.provider_name)
            existing.logo_path = p.get("logo_path", existing.logo_path)
            existing.display_priority = p.get("display_priority", existing.display_priority)
        else:
            db.add(ProviderMaster(
                provider_id=pid,
                provider_name=p.get("provider_name", ""),
                logo_path=p.get("logo_path"),
                display_priority=p.get("display_priority"),
            ))
        count += 1

    db.commit()
    return count
