def test_create_list(client, auth_profile):
    headers, profile_id = auth_profile
    resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "My Watchlist", "list_type": "watchlist"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Watchlist"
    assert data["list_type"] == "watchlist"
    assert data["item_count"] == 0


def test_list_lists(client, auth_profile):
    headers, profile_id = auth_profile
    client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "List A"},
        headers=headers,
    )
    client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "List B"},
        headers=headers,
    )

    resp = client.get(f"/profiles/{profile_id}/lists", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_add_list_item(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Favorites", "list_type": "favorites"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    resp = client.post(
        f"/profiles/{profile_id}/lists/{list_id}/items",
        json={"title_id": seed_movie, "priority": 3},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title_id"] == seed_movie
    assert data["position"] == 1
    assert data["priority"] == 3


def test_add_duplicate_item(client, auth_profile, seed_movie):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Dupes"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    client.post(
        f"/profiles/{profile_id}/lists/{list_id}/items",
        json={"title_id": seed_movie},
        headers=headers,
    )
    resp = client.post(
        f"/profiles/{profile_id}/lists/{list_id}/items",
        json={"title_id": seed_movie},
        headers=headers,
    )
    assert resp.status_code == 409


def test_list_detail(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Detail Test"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    for mid in seed_movies:
        client.post(
            f"/profiles/{profile_id}/lists/{list_id}/items",
            json={"title_id": mid},
            headers=headers,
        )

    resp = client.get(
        f"/profiles/{profile_id}/lists/{list_id}", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    positions = [item["position"] for item in data["items"]]
    assert positions == [1, 2, 3]


def test_reorder_items(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Reorder Test"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    for mid in seed_movies:
        client.post(
            f"/profiles/{profile_id}/lists/{list_id}/items",
            json={"title_id": mid},
            headers=headers,
        )

    # Reverse order
    reversed_ids = list(reversed(seed_movies))
    resp = client.patch(
        f"/profiles/{profile_id}/lists/{list_id}/items/reorder",
        json={"ordered_title_ids": reversed_ids},
        headers=headers,
    )
    assert resp.status_code == 200

    detail = client.get(
        f"/profiles/{profile_id}/lists/{list_id}", headers=headers
    ).json()
    title_ids = [item["title_id"] for item in detail["items"]]
    assert title_ids == reversed_ids


def test_remove_item(client, auth_profile, seed_movies):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Remove Test"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    for mid in seed_movies:
        client.post(
            f"/profiles/{profile_id}/lists/{list_id}/items",
            json={"title_id": mid},
            headers=headers,
        )

    # Remove middle item
    resp = client.delete(
        f"/profiles/{profile_id}/lists/{list_id}/items/{seed_movies[1]}",
        headers=headers,
    )
    assert resp.status_code == 204

    detail = client.get(
        f"/profiles/{profile_id}/lists/{list_id}", headers=headers
    ).json()
    assert len(detail["items"]) == 2
    # Positions should be recompacted
    positions = [item["position"] for item in detail["items"]]
    assert positions == [1, 2]


def test_delete_list(client, auth_profile):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "To Delete"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    resp = client.delete(
        f"/profiles/{profile_id}/lists/{list_id}", headers=headers
    )
    assert resp.status_code == 204

    resp = client.get(f"/profiles/{profile_id}/lists", headers=headers)
    assert len(resp.json()) == 0


def test_update_list_name(client, auth_profile):
    headers, profile_id = auth_profile
    list_resp = client.post(
        f"/profiles/{profile_id}/lists",
        json={"name": "Old Name"},
        headers=headers,
    )
    list_id = list_resp.json()["id"]

    resp = client.patch(
        f"/profiles/{profile_id}/lists/{list_id}",
        json={"name": "New Name"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_list_wrong_profile(client, auth_profile):
    headers, _ = auth_profile
    resp = client.get("/profiles/99999/lists", headers=headers)
    assert resp.status_code == 404
