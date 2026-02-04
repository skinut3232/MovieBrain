def test_log_watch(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    resp = client.post(
        f"/profiles/{profile_id}/watches",
        json={
            "title_id": seed_movie,
            "rating_1_10": 8,
            "notes": "Great movie",
            "rewatch_count": 0,
            "tag_names": ["thriller", "favorite"],
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating_1_10"] == 8
    assert data["notes"] == "Great movie"
    assert len(data["tags"]) == 2
    tag_names = {t["name"] for t in data["tags"]}
    assert tag_names == {"thriller", "favorite"}


def test_log_watch_upsert(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    # First log
    client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movie, "rating_1_10": 5, "tag_names": []},
        headers=headers,
    )
    # Second log (upsert)
    resp = client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movie, "rating_1_10": 9, "tag_names": ["updated"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating_1_10"] == 9
    assert data["tags"][0]["name"] == "updated"


def test_watch_history(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    for mid in seed_movies:
        client.post(
            f"/profiles/{profile_id}/watches",
            json={"title_id": mid, "rating_1_10": 7, "tag_names": []},
            headers=headers,
        )

    resp = client.get(f"/profiles/{profile_id}/history", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["results"]) == 3


def test_watch_history_filter_by_rating(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    for i, mid in enumerate(seed_movies):
        client.post(
            f"/profiles/{profile_id}/watches",
            json={"title_id": mid, "rating_1_10": 3 + i * 3, "tag_names": []},
            headers=headers,
        )

    resp = client.get(
        f"/profiles/{profile_id}/history?min_rating=6", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2


def test_watch_history_filter_by_tag(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movies[0], "rating_1_10": 7, "tag_names": ["scifi"]},
        headers=headers,
    )
    client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movies[1], "rating_1_10": 5, "tag_names": ["drama"]},
        headers=headers,
    )

    resp = client.get(
        f"/profiles/{profile_id}/history?tag=scifi", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["title_id"] == seed_movies[0]


def test_delete_watch(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movie, "tag_names": []},
        headers=headers,
    )

    resp = client.delete(
        f"/profiles/{profile_id}/watches/{seed_movie}", headers=headers
    )
    assert resp.status_code == 204

    resp = client.get(f"/profiles/{profile_id}/history", headers=headers)
    assert resp.json()["total"] == 0


def test_delete_watch_not_found(client, auth_profile):
    headers, profile_id = auth_profile
    resp = client.delete(
        f"/profiles/{profile_id}/watches/99999", headers=headers
    )
    assert resp.status_code == 404


def test_tags_crud(client, auth_profile):
    headers, profile_id = auth_profile

    # Create tag
    resp = client.post(
        f"/profiles/{profile_id}/tags",
        json={"name": "horror"},
        headers=headers,
    )
    assert resp.status_code == 201
    tag_id = resp.json()["id"]

    # List tags
    resp = client.get(f"/profiles/{profile_id}/tags", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "horror"

    # Duplicate tag
    resp = client.post(
        f"/profiles/{profile_id}/tags",
        json={"name": "horror"},
        headers=headers,
    )
    assert resp.status_code == 409

    # Delete tag
    resp = client.delete(f"/profiles/{profile_id}/tags/{tag_id}", headers=headers)
    assert resp.status_code == 204

    # Verify deleted
    resp = client.get(f"/profiles/{profile_id}/tags", headers=headers)
    assert len(resp.json()) == 0


def test_watch_wrong_profile(client, auth_profile, seed_movie):
    """Cannot access watches of a non-existent profile."""
    headers, _ = auth_profile
    resp = client.post(
        "/profiles/99999/watches",
        json={"title_id": seed_movie, "tag_names": []},
        headers=headers,
    )
    assert resp.status_code == 404


def test_watch_rating_validation(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    resp = client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movie, "rating_1_10": 11, "tag_names": []},
        headers=headers,
    )
    assert resp.status_code == 422

    resp = client.post(
        f"/profiles/{profile_id}/watches",
        json={"title_id": seed_movie, "rating_1_10": 0, "tag_names": []},
        headers=headers,
    )
    assert resp.status_code == 422


def test_watch_history_pagination(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    for mid in seed_movies:
        client.post(
            f"/profiles/{profile_id}/watches",
            json={"title_id": mid, "tag_names": []},
            headers=headers,
        )

    resp = client.get(
        f"/profiles/{profile_id}/history?page=1&limit=2", headers=headers
    )
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["total"] == 3

    resp = client.get(
        f"/profiles/{profile_id}/history?page=2&limit=2", headers=headers
    )
    data = resp.json()
    assert len(data["results"]) == 1
