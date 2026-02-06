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
