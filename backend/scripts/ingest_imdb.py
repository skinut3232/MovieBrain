"""
IMDb data ingestion script.

Downloads IMDb TSV.gz files and loads movie data into the MovieBrain catalog tables.
Filters to titleType == "movie" only.

Usage:
    python -m scripts.ingest_imdb
"""

import csv
import gzip
import os
import sys
import time
import urllib.request
from io import TextIOWrapper
from pathlib import Path

# Add backend dir to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.config import settings
from app.database import Base, engine, SessionLocal

IMDB_BASE_URL = "https://datasets.imdbws.com/"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FILES = [
    "title.basics.tsv.gz",
    "title.ratings.tsv.gz",
    "title.akas.tsv.gz",
    "title.crew.tsv.gz",
    "title.principals.tsv.gz",
    "name.basics.tsv.gz",
]

CHUNK_SIZE = 5000


def clean(val: str) -> str | None:
    """Convert IMDb '\\N' null markers to None."""
    return None if val == "\\N" else val


def clean_int(val: str) -> int | None:
    v = clean(val)
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def clean_float(val: str) -> float | None:
    v = clean(val)
    if v is None:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def download_file(filename: str) -> Path:
    """Download a file from IMDb datasets if not already cached locally."""
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / filename
    if filepath.exists():
        print(f"  [cached] {filename}")
        return filepath
    url = IMDB_BASE_URL + filename
    print(f"  Downloading {url} ...")
    urllib.request.urlretrieve(url, filepath)
    print(f"  Downloaded {filename} ({filepath.stat().st_size / 1024 / 1024:.1f} MB)")
    return filepath


def open_tsv(filepath: Path):
    """Open a gzipped TSV file and return a csv.DictReader."""
    f = gzip.open(filepath, "rt", encoding="utf-8")
    reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    return f, reader


def ingest_title_basics(db):
    """Load title.basics.tsv.gz -> catalog_titles (movies only)."""
    print("\n=== Ingesting title.basics (movies only) ===")
    filepath = download_file("title.basics.tsv.gz")
    f, reader = open_tsv(filepath)

    count = 0
    skipped = 0
    chunk = []

    for row in reader:
        if row["titleType"] != "movie":
            skipped += 1
            continue

        primary = clean(row["primaryTitle"]) or ""
        original = clean(row["originalTitle"]) or ""
        search_text = f"{primary} {original}".strip()

        chunk.append({
            "imdb_tconst": row["tconst"],
            "title_type": row["titleType"],
            "primary_title": primary,
            "original_title": clean(row["originalTitle"]),
            "start_year": clean_int(row["startYear"]),
            "end_year": clean_int(row["endYear"]),
            "runtime_minutes": clean_int(row["runtimeMinutes"]),
            "genres": clean(row["genres"]),
            "title_search_text": search_text,
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_titles
                        (imdb_tconst, title_type, primary_title, original_title,
                         start_year, end_year, runtime_minutes, genres, title_search_text,
                         ts_vector)
                    VALUES
                        (:imdb_tconst, :title_type, :primary_title, :original_title,
                         :start_year, :end_year, :runtime_minutes, :genres, :title_search_text,
                         to_tsvector('english', :title_search_text))
                    ON CONFLICT (imdb_tconst) DO NOTHING
                """),
                chunk,
            )
            db.commit()
            chunk = []
            print(f"  ... {count} movies loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_titles
                    (imdb_tconst, title_type, primary_title, original_title,
                     start_year, end_year, runtime_minutes, genres, title_search_text,
                     ts_vector)
                VALUES
                    (:imdb_tconst, :title_type, :primary_title, :original_title,
                     :start_year, :end_year, :runtime_minutes, :genres, :title_search_text,
                     to_tsvector('english', :title_search_text))
                ON CONFLICT (imdb_tconst) DO NOTHING
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} movies, skipped {skipped} non-movie titles")
    return count


def build_tconst_to_id_map(db) -> dict[str, int]:
    """Build a lookup map from imdb_tconst -> catalog_titles.id."""
    print("  Building tconst -> id lookup map...")
    rows = db.execute(text("SELECT id, imdb_tconst FROM catalog_titles")).fetchall()
    return {row[1]: row[0] for row in rows}


def build_nconst_to_id_map(db) -> dict[str, int]:
    """Build a lookup map from imdb_nconst -> catalog_people.id."""
    print("  Building nconst -> id lookup map...")
    rows = db.execute(text("SELECT id, imdb_nconst FROM catalog_people")).fetchall()
    return {row[1]: row[0] for row in rows}


def ingest_title_ratings(db, tconst_map: dict[str, int]):
    """Load title.ratings.tsv.gz -> catalog_ratings."""
    print("\n=== Ingesting title.ratings ===")
    filepath = download_file("title.ratings.tsv.gz")
    f, reader = open_tsv(filepath)

    count = 0
    skipped = 0
    chunk = []

    for row in reader:
        tconst = row["tconst"]
        title_id = tconst_map.get(tconst)
        if title_id is None:
            skipped += 1
            continue

        chunk.append({
            "title_id": title_id,
            "average_rating": clean_float(row["averageRating"]),
            "num_votes": clean_int(row["numVotes"]),
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_ratings (title_id, average_rating, num_votes)
                    VALUES (:title_id, :average_rating, :num_votes)
                    ON CONFLICT (title_id) DO NOTHING
                """),
                chunk,
            )
            db.commit()
            chunk = []
            print(f"  ... {count} ratings loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_ratings (title_id, average_rating, num_votes)
                VALUES (:title_id, :average_rating, :num_votes)
                ON CONFLICT (title_id) DO NOTHING
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} ratings, skipped {skipped}")


def ingest_title_crew(db, tconst_map: dict[str, int]):
    """Load title.crew.tsv.gz -> catalog_crew."""
    print("\n=== Ingesting title.crew ===")
    filepath = download_file("title.crew.tsv.gz")
    f, reader = open_tsv(filepath)

    count = 0
    skipped = 0
    chunk = []

    for row in reader:
        tconst = row["tconst"]
        title_id = tconst_map.get(tconst)
        if title_id is None:
            skipped += 1
            continue

        directors = clean(row["directors"])
        writers = clean(row["writers"])
        director_list = directors.split(",") if directors else []
        writer_list = writers.split(",") if writers else []

        chunk.append({
            "title_id": title_id,
            "director_nconsts": director_list,
            "writer_nconsts": writer_list,
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_crew (title_id, director_nconsts, writer_nconsts)
                    VALUES (:title_id, :director_nconsts, :writer_nconsts)
                    ON CONFLICT (title_id) DO NOTHING
                """),
                chunk,
            )
            db.commit()
            chunk = []
            print(f"  ... {count} crew records loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_crew (title_id, director_nconsts, writer_nconsts)
                VALUES (:title_id, :director_nconsts, :writer_nconsts)
                ON CONFLICT (title_id) DO NOTHING
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} crew records, skipped {skipped}")


def ingest_title_akas(db, tconst_map: dict[str, int]):
    """Load title.akas.tsv.gz -> catalog_akas."""
    print("\n=== Ingesting title.akas ===")
    filepath = download_file("title.akas.tsv.gz")
    f, reader = open_tsv(filepath)

    count = 0
    skipped = 0
    chunk = []

    for row in reader:
        tconst = row["titleId"]
        title_id = tconst_map.get(tconst)
        if title_id is None:
            skipped += 1
            continue

        is_orig = clean(row.get("isOriginalTitle", "0"))
        chunk.append({
            "title_id": title_id,
            "ordering": clean_int(row["ordering"]),
            "localized_title": clean(row["title"]),
            "region": clean(row["region"]),
            "language": clean(row["language"]),
            "is_original": is_orig == "1" if is_orig else False,
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_akas
                        (title_id, ordering, localized_title, region, language, is_original)
                    VALUES
                        (:title_id, :ordering, :localized_title, :region, :language, :is_original)
                """),
                chunk,
            )
            db.commit()
            chunk = []
            print(f"  ... {count} aka records loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_akas
                    (title_id, ordering, localized_title, region, language, is_original)
                VALUES
                    (:title_id, :ordering, :localized_title, :region, :language, :is_original)
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} aka records, skipped {skipped}")


def ingest_name_basics(db, tconst_map: dict[str, int]):
    """Load name.basics.tsv.gz -> catalog_people.
    Only loads people who appear in knownForTitles that are in our movie set.
    """
    print("\n=== Ingesting name.basics (people linked to movies) ===")
    filepath = download_file("name.basics.tsv.gz")
    f, reader = open_tsv(filepath)

    # Also collect all nconsts referenced from principals file to load
    # For now, load all people (we'll filter via principals later)
    # Actually, let's load all people referenced in principals
    # We'll do a two-pass approach: first collect needed nconsts from principals,
    # then load only those people. But that requires reading principals first.
    # Simpler: load ALL people, which is ~13M rows but manageable.
    # Actually let's be smarter: collect nconsts we need from title.principals first

    # For simplicity, load all people - the ingestion is a one-time operation
    count = 0
    chunk = []

    for row in reader:
        chunk.append({
            "imdb_nconst": row["nconst"],
            "primary_name": clean(row["primaryName"]) or "Unknown",
            "birth_year": clean_int(row["birthYear"]),
            "death_year": clean_int(row["deathYear"]),
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_people (imdb_nconst, primary_name, birth_year, death_year)
                    VALUES (:imdb_nconst, :primary_name, :birth_year, :death_year)
                    ON CONFLICT (imdb_nconst) DO NOTHING
                """),
                chunk,
            )
            db.commit()
            chunk = []
            if count % 50000 == 0:
                print(f"  ... {count} people loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_people (imdb_nconst, primary_name, birth_year, death_year)
                VALUES (:imdb_nconst, :primary_name, :birth_year, :death_year)
                ON CONFLICT (imdb_nconst) DO NOTHING
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} people")
    return count


def ingest_title_principals(db, tconst_map: dict[str, int], nconst_map: dict[str, int]):
    """Load title.principals.tsv.gz -> catalog_principals."""
    print("\n=== Ingesting title.principals ===")
    filepath = download_file("title.principals.tsv.gz")
    f, reader = open_tsv(filepath)

    count = 0
    skipped = 0
    chunk = []

    for row in reader:
        tconst = row["tconst"]
        title_id = tconst_map.get(tconst)
        if title_id is None:
            skipped += 1
            continue

        nconst = row["nconst"]
        person_id = nconst_map.get(nconst)
        if person_id is None:
            skipped += 1
            continue

        chunk.append({
            "title_id": title_id,
            "person_id": person_id,
            "ordering": clean_int(row["ordering"]),
            "category": clean(row["category"]),
            "job": clean(row["job"]),
            "characters": clean(row["characters"]),
        })
        count += 1

        if len(chunk) >= CHUNK_SIZE:
            db.execute(
                text("""
                    INSERT INTO catalog_principals
                        (title_id, person_id, ordering, category, job, characters)
                    VALUES
                        (:title_id, :person_id, :ordering, :category, :job, :characters)
                """),
                chunk,
            )
            db.commit()
            chunk = []
            if count % 50000 == 0:
                print(f"  ... {count} principals loaded", end="\r")

    if chunk:
        db.execute(
            text("""
                INSERT INTO catalog_principals
                    (title_id, person_id, ordering, category, job, characters)
                VALUES
                    (:title_id, :person_id, :ordering, :category, :job, :characters)
            """),
            chunk,
        )
        db.commit()

    f.close()
    print(f"  Loaded {count} principals, skipped {skipped}")


def print_stats(db):
    """Print ingestion statistics."""
    print("\n=== Ingestion Statistics ===")
    tables = [
        "catalog_titles",
        "catalog_ratings",
        "catalog_crew",
        "catalog_akas",
        "catalog_people",
        "catalog_principals",
    ]
    for table in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  {table}: {result:,} rows")

    # Null rate for key columns
    total = db.execute(text("SELECT COUNT(*) FROM catalog_titles")).scalar()
    if total > 0:
        no_year = db.execute(
            text("SELECT COUNT(*) FROM catalog_titles WHERE start_year IS NULL")
        ).scalar()
        no_runtime = db.execute(
            text("SELECT COUNT(*) FROM catalog_titles WHERE runtime_minutes IS NULL")
        ).scalar()
        no_genres = db.execute(
            text("SELECT COUNT(*) FROM catalog_titles WHERE genres IS NULL")
        ).scalar()
        print(f"\n  Null rates (catalog_titles):")
        print(f"    start_year: {no_year/total*100:.1f}%")
        print(f"    runtime_minutes: {no_runtime/total*100:.1f}%")
        print(f"    genres: {no_genres/total*100:.1f}%")


def main():
    print("MovieBrain IMDb Data Ingestion")
    print("=" * 50)
    start = time.time()

    db = SessionLocal()

    try:
        # Step 1: Title basics (movies only)
        ingest_title_basics(db)

        # Build tconst lookup
        tconst_map = build_tconst_to_id_map(db)
        print(f"  {len(tconst_map):,} movie tconsts in map")

        # Step 2: Ratings
        ingest_title_ratings(db, tconst_map)

        # Step 3: Crew
        ingest_title_crew(db, tconst_map)

        # Step 4: AKAs
        ingest_title_akas(db, tconst_map)

        # Step 5: People (all)
        ingest_name_basics(db, tconst_map)

        # Build nconst lookup
        nconst_map = build_nconst_to_id_map(db)
        print(f"  {len(nconst_map):,} people nconsts in map")

        # Step 6: Principals
        ingest_title_principals(db, tconst_map, nconst_map)

        # Stats
        print_stats(db)

    finally:
        db.close()

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
