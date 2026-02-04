def test_create_flag(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    resp = client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movie, "flag_type": "not_interested"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title_id"] == seed_movie
    assert data["flag_type"] == "not_interested"


def test_flag_upsert(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movie, "flag_type": "not_interested"},
        headers=headers,
    )
    # Change flag type
    resp = client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movie, "flag_type": "dont_recommend"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["flag_type"] == "dont_recommend"

    # Only one flag should exist
    resp = client.get(f"/profiles/{profile_id}/flags", headers=headers)
    assert len(resp.json()) == 1


def test_delete_flag(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movie, "flag_type": "not_interested"},
        headers=headers,
    )

    resp = client.delete(
        f"/profiles/{profile_id}/flags/{seed_movie}", headers=headers
    )
    assert resp.status_code == 204

    resp = client.get(f"/profiles/{profile_id}/flags", headers=headers)
    assert len(resp.json()) == 0


def test_delete_flag_not_found(client, auth_profile):
    headers, profile_id = auth_profile
    resp = client.delete(
        f"/profiles/{profile_id}/flags/99999", headers=headers
    )
    assert resp.status_code == 404


def test_list_flags(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movies[0], "flag_type": "not_interested"},
        headers=headers,
    )
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movies[1], "flag_type": "dont_recommend"},
        headers=headers,
    )

    resp = client.get(f"/profiles/{profile_id}/flags", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_flags_filter_by_type(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movies[0], "flag_type": "not_interested"},
        headers=headers,
    )
    client.post(
        f"/profiles/{profile_id}/flags",
        json={"title_id": seed_movies[1], "flag_type": "dont_recommend"},
        headers=headers,
    )

    resp = client.get(
        f"/profiles/{profile_id}/flags?flag_type=not_interested",
        headers=headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["flag_type"] == "not_interested"


def test_flags_wrong_profile(client, auth_profile, seed_movie):
    headers, _ = auth_profile
    resp = client.post(
        "/profiles/99999/flags",
        json={"title_id": seed_movie, "flag_type": "not_interested"},
        headers=headers,
    )
    assert resp.status_code == 404
