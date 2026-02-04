def test_register(client):
    resp = client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "secret123"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "secret123"})
    assert resp.status_code == 409


def test_login(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "mypass"})
    resp = client.post("/auth/login", data={"username": "login@example.com", "password": "mypass"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "right"})
    resp = client.post("/auth/login", data={"username": "wrong@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent(client):
    resp = client.post("/auth/login", data={"username": "nope@example.com", "password": "x"})
    assert resp.status_code == 401


def test_protected_endpoint_no_token(client):
    resp = client.get("/profiles")
    assert resp.status_code == 401


def test_protected_endpoint_with_token(client):
    reg = client.post("/auth/register", json={"email": "auth@example.com", "password": "pass"})
    token = reg.json()["access_token"]
    resp = client.get("/profiles", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_profiles_crud(client):
    # Register
    reg = client.post("/auth/register", json={"email": "crud@example.com", "password": "pass"})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile
    resp = client.post("/profiles", json={"name": "My Profile"}, headers=headers)
    assert resp.status_code == 201
    profile = resp.json()
    assert profile["name"] == "My Profile"
    profile_id = profile["id"]

    # List profiles
    resp = client.get("/profiles", headers=headers)
    assert resp.status_code == 200
    profiles = resp.json()
    assert len(profiles) == 1

    # Update profile
    resp = client.patch(f"/profiles/{profile_id}", json={"name": "Renamed"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"

    # Delete profile
    resp = client.delete(f"/profiles/{profile_id}", headers=headers)
    assert resp.status_code == 204

    # Verify deleted
    resp = client.get("/profiles", headers=headers)
    assert len(resp.json()) == 0
