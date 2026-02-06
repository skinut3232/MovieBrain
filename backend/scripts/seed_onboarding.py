"""Seed the onboarding_movies table with ~100 well-known, genre-balanced movies.

Usage:
    cd backend
    python -m scripts.seed_onboarding

Selection criteria:
  - Must have embeddings (so ratings feed into taste vector)
  - Top movies by num_votes from catalog_ratings
  - Genre-balanced: ~10-12 per major genre
  - Well-known, broadly-seen movies
"""
import sys

from sqlalchemy import text

sys.path.insert(0, ".")
from app.database import SessionLocal

GENRES = [
    "Action",
    "Comedy",
    "Drama",
    "Sci-Fi",
    "Horror",
    "Thriller",
    "Romance",
    "Animation",
    "Crime",
    "Adventure",
]

MOVIES_PER_GENRE = 12


def main():
    db = SessionLocal()

    # Clear existing onboarding movies
    db.execute(text("DELETE FROM onboarding_movies"))
    db.commit()

    selected_ids = set()
    display_order = 1

    for genre in GENRES:
        # Get top movies for this genre by vote count, that have embeddings
        rows = db.execute(
            text("""
                SELECT ct.id, ct.primary_title, ct.start_year, cr.num_votes
                FROM catalog_titles ct
                JOIN catalog_ratings cr ON cr.title_id = ct.id
                JOIN movie_embeddings me ON me.title_id = ct.id
                WHERE ct.title_type = 'movie'
                  AND ct.genres ILIKE :genre_pattern
                  AND cr.num_votes >= 50000
                  AND ct.id != ALL(:excluded)
                ORDER BY cr.num_votes DESC
                LIMIT :limit
            """),
            {
                "genre_pattern": f"%{genre}%",
                "excluded": list(selected_ids) if selected_ids else [0],
                "limit": MOVIES_PER_GENRE,
            },
        ).fetchall()

        if not rows:
            # Fallback: try without embedding requirement
            rows = db.execute(
                text("""
                    SELECT ct.id, ct.primary_title, ct.start_year, cr.num_votes
                    FROM catalog_titles ct
                    JOIN catalog_ratings cr ON cr.title_id = ct.id
                    WHERE ct.title_type = 'movie'
                      AND ct.genres ILIKE :genre_pattern
                      AND cr.num_votes >= 50000
                      AND ct.id != ALL(:excluded)
                    ORDER BY cr.num_votes DESC
                    LIMIT :limit
                """),
                {
                    "genre_pattern": f"%{genre}%",
                    "excluded": list(selected_ids) if selected_ids else [0],
                    "limit": MOVIES_PER_GENRE,
                },
            ).fetchall()

        print(f"\n{genre} ({len(rows)} movies):")
        for title_id, title, year, votes in rows:
            print(f"  {title} ({year}) - {votes:,} votes")
            selected_ids.add(title_id)
            db.execute(
                text("""
                    INSERT INTO onboarding_movies (title_id, display_order)
                    VALUES (:title_id, :display_order)
                """),
                {"title_id": title_id, "display_order": display_order},
            )
            display_order += 1

    db.commit()
    db.close()

    print(f"\nSeeded {len(selected_ids)} onboarding movies.")


if __name__ == "__main__":
    main()
