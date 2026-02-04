"""Tests for the recommendation system (Milestone 3)."""


def _log_watch(client, headers, profile_id, title_id, rating):
    """Helper to log a watch with a rating."""
    return client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": title_id, "rating_1_10": rating},
        headers=headers,
    )


def test_popularity_fallback_when_few_ratings(
    client, auth_profile, seed_movies_with_embeddings
):
    """When profile has < 5 rated movies, should use popularity fallback."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Rate only 2 movies (below threshold of 5)
    _log_watch(client, headers, profile_id, ids[0], 8)
    _log_watch(client, headers, profile_id, ids[1], 7)

    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["fallback_mode"] is True
    assert len(data["results"]) > 0
    # Similarity score should be null in fallback mode
    for r in data["results"]:
        assert r["similarity_score"] is None


def test_personalized_results_with_taste_vector(
    client, auth_profile, seed_movies_with_embeddings
):
    """When profile has >= 5 rated movies, should get personalized results."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Rate 6 movies to exceed threshold
    for i in range(6):
        _log_watch(client, headers, profile_id, ids[i], 7 + (i % 4))

    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["fallback_mode"] is False
    assert len(data["results"]) > 0
    # Similarity scores should be present in personalized mode
    for r in data["results"]:
        assert r["similarity_score"] is not None


def test_excludes_watched_movies(
    client, auth_profile, seed_movies_with_embeddings
):
    """Watched movies should not appear in recommendations."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Watch several movies (some rated, some not)
    watched_ids = set()
    for i in range(6):
        _log_watch(client, headers, profile_id, ids[i], 8)
        watched_ids.add(ids[i])

    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    result_ids = {r["title_id"] for r in data["results"]}
    # No watched movie should appear in results
    assert result_ids.isdisjoint(watched_ids)


def test_excludes_flagged_movies(
    client, auth_profile, seed_movies_with_embeddings
):
    """Flagged movies should not appear in recommendations."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Rate enough movies for personalized mode
    for i in range(6):
        _log_watch(client, headers, profile_id, ids[i], 8)

    # Flag a movie that we haven't watched
    flagged_id = ids[7]
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": flagged_id, "flag_type": "dont_recommend"},
        headers=headers,
    )

    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    result_ids = {r["title_id"] for r in data["results"]}
    assert flagged_id not in result_ids


def test_genre_filter(client, auth_profile, seed_movies_with_embeddings):
    """Genre filter should narrow results."""
    headers, profile_id = auth_profile

    # Use fallback mode (no ratings) with genre filter
    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={"genre": "Action"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    for r in data["results"]:
        assert "Action" in (r["genres"] or "")


def test_year_filter(client, auth_profile, seed_movies_with_embeddings):
    """Year filter should narrow results."""
    headers, profile_id = auth_profile

    resp = client.post(
        f"/profiles/{profile_id}/recommend",
        json={"min_year": 2005, "max_year": 2007},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    for r in data["results"]:
        assert 2005 <= r["start_year"] <= 2007


def test_pagination(client, auth_profile, seed_movies_with_embeddings):
    """Pagination should return correct page of results."""
    headers, profile_id = auth_profile

    # Get page 1 with limit 3
    resp1 = client.post(
        f"/profiles/{profile_id}/recommend",
        json={"limit": 3, "page": 1},
        headers=headers,
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["results"]) == 3
    assert data1["page"] == 1
    assert data1["limit"] == 3

    # Get page 2 with limit 3
    resp2 = client.post(
        f"/profiles/{profile_id}/recommend",
        json={"limit": 3, "page": 2},
        headers=headers,
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["page"] == 2

    # Results should differ between pages
    ids1 = {r["title_id"] for r in data1["results"]}
    ids2 = {r["title_id"] for r in data2["results"]}
    assert ids1.isdisjoint(ids2)


def test_taste_profile_endpoint(
    client, auth_profile, seed_movies_with_embeddings
):
    """Taste profile endpoint should return correct status."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Before any ratings
    resp = client.get(
        f"/profiles/{profile_id}/taste",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_taste_vector"] is False
    assert data["num_rated_movies"] == 0
    assert data["min_required"] == 5

    # Rate 6 movies
    for i in range(6):
        _log_watch(client, headers, profile_id, ids[i], 8)

    resp = client.get(
        f"/profiles/{profile_id}/taste",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["num_rated_movies"] == 6


def test_recompute_taste_endpoint(
    client, auth_profile, seed_movies_with_embeddings
):
    """Recompute taste endpoint should create/update the taste vector."""
    headers, profile_id = auth_profile
    ids = seed_movies_with_embeddings

    # Rate 6 movies
    for i in range(6):
        _log_watch(client, headers, profile_id, ids[i], 7 + i % 3)

    resp = client.post(
        f"/profiles/{profile_id}/taste/recompute",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_taste_vector"] is True
    assert data["num_rated_movies"] == 6
    assert data["updated_at"] is not None


def test_wrong_profile_returns_404(client, auth_profile):
    """Accessing recommendations for a non-existent profile should return 404."""
    headers, _ = auth_profile

    resp = client.post(
        "/profiles/99999/recommend",
        json={},
        headers=headers,
    )
    assert resp.status_code == 404
