import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    # Register a new user
    response = client.post("/auth/register", json={
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpass123",
        "role": "user"
    })
    assert response.status_code == 200 or response.status_code == 400  # 400 if already exists

    # Login with the new user
    response = client.post("/auth/login", data={
        "username": "testuser@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Get current user
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == "testuser@example.com"
    assert user["username"] == "testuser"
