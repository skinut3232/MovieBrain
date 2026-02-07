from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.catalog import CatalogRating, CatalogTitle

OMDB_CACHE_DAYS = 90


def parse_rt_percentage(value: str | None) -> int | None:
    """Parse '93%' -> 93, 'N/A' or None -> None."""
    if not value or value == "N/A":
        return None
    try:
        return int(value.rstrip("%"))
    except (ValueError, TypeError):
        return None


def parse_metacritic(value: str | None) -> int | None:
    """Parse '84/100' -> 84, 'N/A' or None -> None."""
    if not value or value == "N/A":
        return None
    try:
        return int(value.split("/")[0])
    except (ValueError, TypeError, IndexError):
        return None


def fetch_omdb_ratings(imdb_id: str) -> dict | None:
    """Call OMDb API and extract RT + Metacritic scores.

    Returns dict with rt_critic_score, rt_audience_score, metacritic_score,
    or None on API error.
    """
    if not settings.OMDB_API_KEY:
        return None

    url = "http://www.omdbapi.com/"
    params = {"apikey": settings.OMDB_API_KEY, "i": imdb_id}

    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    if data.get("Response") == "False":
        # Movie not found in OMDb — return empty scores, not error
        return {"rt_critic_score": None, "rt_audience_score": None, "metacritic_score": None}

    rt_critic_score = None
    metacritic_score = None

    # Parse the Ratings array
    for rating in data.get("Ratings", []):
        source = rating.get("Source", "")
        value = rating.get("Value", "")
        if source == "Rotten Tomatoes":
            rt_critic_score = parse_rt_percentage(value)
        elif source == "Metacritic":
            metacritic_score = parse_metacritic(value)

    # Fallback: use top-level Metascore field if Ratings array didn't have it
    if metacritic_score is None:
        metacritic_score = parse_metacritic(data.get("Metascore"))

    return {
        "rt_critic_score": rt_critic_score,
        "rt_audience_score": None,  # OMDb doesn't provide this today
        "metacritic_score": metacritic_score,
    }


def get_or_fetch_omdb_ratings(db: Session, title: CatalogTitle) -> dict:
    """Return cached OMDb ratings, or fetch and cache them.

    Returns dict with rt_critic_score, rt_audience_score, metacritic_score.
    """
    rating = title.rating
    if not rating:
        return {"rt_critic_score": None, "rt_audience_score": None, "metacritic_score": None}

    # Check if cache is fresh
    if rating.omdb_fetched_at is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=OMDB_CACHE_DAYS)
        if rating.omdb_fetched_at > cutoff:
            return {
                "rt_critic_score": rating.rt_critic_score,
                "rt_audience_score": rating.rt_audience_score,
                "metacritic_score": rating.metacritic_score,
            }

    # Fetch from OMDb
    scores = fetch_omdb_ratings(title.imdb_tconst)
    if scores is None:
        # API error — return whatever we have cached (may be None)
        return {
            "rt_critic_score": rating.rt_critic_score,
            "rt_audience_score": rating.rt_audience_score,
            "metacritic_score": rating.metacritic_score,
        }

    # Store in DB
    rating.rt_critic_score = scores["rt_critic_score"]
    rating.rt_audience_score = scores["rt_audience_score"]
    rating.metacritic_score = scores["metacritic_score"]
    rating.omdb_fetched_at = datetime.now(timezone.utc)
    db.commit()

    return scores
