import pytest
from app.models import UserRole


def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={"user_id": "emp1", "password": "pass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["user_id"] == "emp1"
    assert data["user"]["role"] == "employee"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"user_id": "emp1", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_missing_user(client):
    response = client.post(
        "/auth/login",
        json={"user_id": "nonexistent", "password": "pass"}
    )
    assert response.status_code == 401


def test_get_current_user(client, employee_token):
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "emp1"
    assert data["role"] == "employee"


def test_get_current_user_missing_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401


def test_get_current_user_invalid_header_format(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "invalid"}
    )
    assert response.status_code == 401
