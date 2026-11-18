import uuid
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_successful_login(client):
    response = client.post(
        "/api/login",
        json={"username": "alice", "password": "alice123"}
    )

    assert response.status_code == 200


def test_wrong_password(client):
    response = client.post(
        "/api/login",
        json={"username": "alice", "password": "wrong123"}
    )

    assert response.status_code == 401


def test_unknown_username(client):
    response = client.post(
        "/api/login",
        json={"username": "charles", "password": "wrong123"}
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"


def test_unauthenticated_profile(client):
    response = client.get("/api/profile")

    assert response.status_code == 401


def test_authenticated_profile(client):
    client.post(
        "/api/login",
        json={"username": "alice", "password": "alice123"}
    )

    response = client.get("/api/profile")

    assert response.status_code == 200
    assert response.json["username"] == "alice"


def test_logout(client):
    client.post(
        "/api/login",
        json={"username": "alice", "password": "alice123"}
    )

    response = client.post("/api/logout")

    assert response.status_code == 200

    profile = client.get("/api/profile")

    assert profile.status_code == 401

def test_login_rate_limit(client):
    responses = []

    # Give this test a unique IP address
    test_ip = str(uuid.uuid4())

    for _ in range(6):
        response = client.post(
            "/api/login",
            json={"username": "alice", "password": "wrong123"},
            environ_base={"REMOTE_ADDR": test_ip}
        )

        responses.append(response.status_code)

    assert responses[:5] == [401, 401, 401, 401, 401]
    assert responses[5] == 429
