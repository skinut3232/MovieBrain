import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.catalog import CatalogTitle


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
    except Exception:
        pass

    return None


def fetch_movie_details_from_tmdb(imdb_id: str) -> dict | None:
    """Fetch full movie details from TMDb API using an IMDb ID.

    Uses the "find by external ID" endpoint to get TMDb ID,
    then fetches movie details with videos appended.
    Returns dict with poster_path, overview, trailer_key (or None for each).
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
        result = {"poster_path": None, "overview": None, "trailer_key": None}

        # Check movie_results first, then tv_results
        for key, mtype in [("movie_results", "movie"), ("tv_results", "tv")]:
            results = find_data.get(key, [])
            if results:
                item = results[0]
                tmdb_id = item.get("id")
                media_type = mtype
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

    except Exception:
        pass

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

    Fetches poster_path, overview, and trailer_key if not already cached.
    Returns dict with poster_path, overview, trailer_key.
    """
    needs_fetch = (
        title.poster_path is None
        or title.overview is None
        or title.trailer_key is None
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
