from sqlalchemy import text


def _seed_movie(db, tconst="tt0000001", title="Test Movie", year=2020, genres="Action"):
    """Insert a test movie directly into the database."""
    db.execute(
        text("""
            INSERT INTO catalog_titles
                (imdb_tconst, title_type, primary_title, original_title,
                 start_year, runtime_minutes, genres, title_search_text, ts_vector)
            VALUES
                (:tconst, 'movie', :title, :title,
                 :year, 120, :genres, :title,
                 to_tsvector('english', :title))
            RETURNING id
        """),
        {"tconst": tconst, "title": title, "year": year, "genres": genres},
    )
    result = db.execute(text("SELECT lastval()")).scalar()
    db.flush()
    return result


def _seed_rating(db, title_id, rating=8.0, votes=10000):
    db.execute(
        text("""
            INSERT INTO catalog_ratings (title_id, average_rating, num_votes)
            VALUES (:title_id, :rating, :votes)
        """),
        {"title_id": title_id, "rating": rating, "votes": votes},
    )
    db.flush()


def test_search_returns_results(client, db):
    title_id = _seed_movie(db, "tt1234567", "Inception", 2010, "Sci-Fi,Action")
    _seed_rating(db, title_id, 8.8, 2000000)

    resp = client.get("/catalog/search?q=inception")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["results"][0]["primary_title"] == "Inception"
    assert data["results"][0]["average_rating"] == 8.8


def test_search_with_year_filter(client, db):
    _seed_movie(db, "tt0000010", "The Matrix", 1999, "Sci-Fi")
    _seed_movie(db, "tt0000011", "The Matrix Reloaded", 2003, "Sci-Fi")

    resp = client.get("/catalog/search?q=matrix&year=1999")
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["start_year"] == 1999


def test_search_no_results(client, db):
    resp = client.get("/catalog/search?q=xyznonexistenttitle123")
    data = resp.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_search_pagination(client, db):
    for i in range(5):
        _seed_movie(db, f"tt900000{i}", f"Paginated Movie {i}", 2020)

    resp = client.get("/catalog/search?q=paginated&limit=2&page=1")
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["page"] == 1

    resp2 = client.get("/catalog/search?q=paginated&limit=2&page=2")
    data2 = resp2.json()
    assert len(data2["results"]) == 2
    assert data2["page"] == 2


def test_get_title_detail(client, db):
    title_id = _seed_movie(db, "tt5555555", "Detail Movie", 2021, "Drama")
    _seed_rating(db, title_id, 7.5, 5000)

    resp = client.get(f"/catalog/titles/{title_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_title"] == "Detail Movie"
    assert data["rating"]["average_rating"] == 7.5


def test_get_title_not_found(client, db):
    resp = client.get("/catalog/titles/999999")
    assert resp.status_code == 404
