import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    # Register and login a user
    client.post("/auth/register", json={
        "email": "postuser@example.com",
        "username": "postuser",
        "password": "postpass123",
        "role": "user"
    })
    response = client.post("/auth/login", data={
        "username": "postuser@example.com",
        "password": "postpass123"
    })
    return response.json()["access_token"]

def test_create_and_get_post():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Create a post
    response = client.post("/posts/", json={
        "title": "Test Post",
        "content": "This is a test post."
    }, headers=headers)
    assert response.status_code == 200
    post = response.json()
    assert post["title"] == "Test Post"
    # Get posts
    response = client.get("/posts/", headers=headers)
    assert response.status_code == 200
    posts = response.json()
    assert any(p["title"] == "Test Post" for p in posts)
