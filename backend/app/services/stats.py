import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.stats import (
    CriticComparison,
    DecadeCount,
    GenreCount,
    LanguageCount,
    MonthCount,
    MonthRating,
    PersonStat,
    ProfileStats,
    RatedMovie,
    RatingBucket,
)
from app.services.tmdb import get_poster_url

logger = logging.getLogger(__name__)


def get_profile_stats(db: Session, profile_id: int) -> ProfileStats:
    """Compute aggregate stats for a profile's watch history."""
    params = {"profile_id": profile_id}

    # 1. Hero stats
    hero = db.execute(
        text("""
            SELECT
                COUNT(*),
                AVG(w.rating_1_10),
                COALESCE(SUM(ct.runtime_minutes), 0),
                COUNT(DISTINCT ct.original_language),
                COALESCE(SUM(w.rewatch_count), 0)
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id
        """),
        params,
    ).fetchone()

    total_movies = hero[0] or 0
    if total_movies == 0:
        return ProfileStats()

    avg_rating = round(float(hero[1]), 2) if hero[1] is not None else None
    total_runtime = int(hero[2])
    unique_languages = hero[3] or 0
    total_rewatches = int(hero[4])

    # 2. Rating distribution (1-10)
    rating_rows = db.execute(
        text("""
            SELECT rating_1_10, COUNT(*)
            FROM watches
            WHERE profile_id = :profile_id AND rating_1_10 IS NOT NULL
            GROUP BY rating_1_10
            ORDER BY rating_1_10
        """),
        params,
    ).fetchall()
    rating_map = {row[0]: row[1] for row in rating_rows}
    rating_distribution = [
        RatingBucket(rating=i, count=rating_map.get(i, 0)) for i in range(1, 11)
    ]

    # 3. Genre breakdown
    genre_rows = db.execute(
        text("""
            SELECT TRIM(g) AS genre, COUNT(*) AS cnt
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id,
            LATERAL unnest(string_to_array(ct.genres, ',')) AS g
            WHERE w.profile_id = :profile_id AND ct.genres IS NOT NULL
            GROUP BY TRIM(g)
            ORDER BY cnt DESC
        """),
        params,
    ).fetchall()
    genre_breakdown = []
    other_count = 0
    for i, row in enumerate(genre_rows):
        if i < 15:
            genre_breakdown.append(GenreCount(genre=row[0], count=row[1]))
        else:
            other_count += row[1]
    if other_count > 0:
        genre_breakdown.append(GenreCount(genre="Other", count=other_count))

    # 4. Top directors
    director_rows = db.execute(
        text("""
            SELECT cp2.id, cp2.primary_name, COUNT(*) AS cnt,
                   AVG(w.rating_1_10) AS avg_r
            FROM watches w
            JOIN catalog_principals cp ON cp.title_id = w.title_id
            JOIN catalog_people cp2 ON cp2.id = cp.person_id
            WHERE w.profile_id = :profile_id AND cp.category = 'director'
            GROUP BY cp2.id, cp2.primary_name
            ORDER BY cnt DESC, avg_r DESC NULLS LAST
            LIMIT 10
        """),
        params,
    ).fetchall()
    top_directors = [
        PersonStat(
            person_id=row[0],
            name=row[1],
            count=row[2],
            avg_rating=round(float(row[3]), 1) if row[3] is not None else None,
        )
        for row in director_rows
    ]

    # 5. Top actors
    actor_rows = db.execute(
        text("""
            SELECT cp2.id, cp2.primary_name, COUNT(*) AS cnt,
                   AVG(w.rating_1_10) AS avg_r
            FROM watches w
            JOIN catalog_principals cp ON cp.title_id = w.title_id
            JOIN catalog_people cp2 ON cp2.id = cp.person_id
            WHERE w.profile_id = :profile_id
              AND cp.category IN ('actor', 'actress')
            GROUP BY cp2.id, cp2.primary_name
            ORDER BY cnt DESC, avg_r DESC NULLS LAST
            LIMIT 10
        """),
        params,
    ).fetchall()
    top_actors = [
        PersonStat(
            person_id=row[0],
            name=row[1],
            count=row[2],
            avg_rating=round(float(row[3]), 1) if row[3] is not None else None,
        )
        for row in actor_rows
    ]

    # 6. You vs Critics
    critic_rows = db.execute(
        text("""
            SELECT
                ct.id,
                ct.primary_title,
                w.rating_1_10 * 10.0 AS user_score,
                COALESCE(cr.rt_critic_score, cr.average_rating * 10) AS critic_score
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            JOIN catalog_ratings cr ON cr.title_id = ct.id
            WHERE w.profile_id = :profile_id
              AND w.rating_1_10 IS NOT NULL
              AND (cr.rt_critic_score IS NOT NULL OR cr.average_rating IS NOT NULL)
        """),
        params,
    ).fetchall()
    critic_comparisons = [
        CriticComparison(
            title_id=row[0],
            primary_title=row[1],
            user_score=float(row[2]),
            critic_score=float(row[3]),
        )
        for row in critic_rows
    ]
    avg_user_score = None
    avg_critic_score = None
    avg_difference = None
    if critic_comparisons:
        avg_user_score = round(
            sum(c.user_score for c in critic_comparisons) / len(critic_comparisons), 1
        )
        avg_critic_score = round(
            sum(c.critic_score for c in critic_comparisons) / len(critic_comparisons), 1
        )
        avg_difference = round(avg_user_score - avg_critic_score, 1)

    # 7. Movies per month
    month_rows = db.execute(
        text("""
            SELECT TO_CHAR(watched_date, 'YYYY-MM') AS m, COUNT(*)
            FROM watches
            WHERE profile_id = :profile_id AND watched_date IS NOT NULL
            GROUP BY m
            ORDER BY m
        """),
        params,
    ).fetchall()
    movies_per_month = [MonthCount(month=row[0], count=row[1]) for row in month_rows]

    # 8. Rating over time
    rating_time_rows = db.execute(
        text("""
            SELECT TO_CHAR(watched_date, 'YYYY-MM') AS m, AVG(rating_1_10)
            FROM watches
            WHERE profile_id = :profile_id
              AND watched_date IS NOT NULL
              AND rating_1_10 IS NOT NULL
            GROUP BY m
            ORDER BY m
        """),
        params,
    ).fetchall()
    rating_over_time = [
        MonthRating(month=row[0], avg_rating=round(float(row[1]), 1))
        for row in rating_time_rows
    ]

    # 9. Decade distribution
    decade_rows = db.execute(
        text("""
            SELECT (ct.start_year / 10) * 10 AS decade, COUNT(*)
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id AND ct.start_year IS NOT NULL
            GROUP BY decade
            ORDER BY decade
        """),
        params,
    ).fetchall()
    decade_distribution = [
        DecadeCount(decade=row[0], count=row[1]) for row in decade_rows
    ]

    # 10. Highest and lowest rated
    highest_rows = db.execute(
        text("""
            SELECT ct.id, ct.primary_title, ct.start_year,
                   w.rating_1_10, ct.poster_path
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
            ORDER BY w.rating_1_10 DESC, w.updated_at DESC
            LIMIT 5
        """),
        params,
    ).fetchall()
    highest_rated = [
        RatedMovie(
            title_id=row[0],
            primary_title=row[1],
            start_year=row[2],
            rating=row[3],
            poster_url=get_poster_url(row[4]),
        )
        for row in highest_rows
    ]

    lowest_rows = db.execute(
        text("""
            SELECT ct.id, ct.primary_title, ct.start_year,
                   w.rating_1_10, ct.poster_path
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id AND w.rating_1_10 IS NOT NULL
            ORDER BY w.rating_1_10 ASC, w.updated_at DESC
            LIMIT 5
        """),
        params,
    ).fetchall()
    lowest_rated = [
        RatedMovie(
            title_id=row[0],
            primary_title=row[1],
            start_year=row[2],
            rating=row[3],
            poster_url=get_poster_url(row[4]),
        )
        for row in lowest_rows
    ]

    # 11. Language diversity
    lang_rows = db.execute(
        text("""
            SELECT ct.original_language, COUNT(*) AS cnt
            FROM watches w
            JOIN catalog_titles ct ON ct.id = w.title_id
            WHERE w.profile_id = :profile_id
              AND ct.original_language IS NOT NULL
              AND ct.original_language != ''
            GROUP BY ct.original_language
            ORDER BY cnt DESC
            LIMIT 10
        """),
        params,
    ).fetchall()
    language_diversity = [
        LanguageCount(language=row[0], count=row[1]) for row in lang_rows
    ]

    return ProfileStats(
        total_movies=total_movies,
        avg_rating=avg_rating,
        total_runtime_minutes=total_runtime,
        unique_languages=unique_languages,
        total_rewatches=total_rewatches,
        rating_distribution=rating_distribution,
        genre_breakdown=genre_breakdown,
        top_directors=top_directors,
        top_actors=top_actors,
        critic_comparisons=critic_comparisons,
        avg_user_score=avg_user_score,
        avg_critic_score=avg_critic_score,
        avg_difference=avg_difference,
        movies_per_month=movies_per_month,
        rating_over_time=rating_over_time,
        decade_distribution=decade_distribution,
        highest_rated=highest_rated,
        lowest_rated=lowest_rated,
        language_diversity=language_diversity,
    )
