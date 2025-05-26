import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.app.models.user import UserRole

def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["role"] == "PATIENT"
    assert "id" in data
    assert "blockchain_address" in data
    assert data["is_active"] is True

def test_register_duplicate_email(client: TestClient):
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_duplicate_username(client: TestClient):
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test1@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    
    # Try to register with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test2@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_login_success(client: TestClient):
    # Register a user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    
    # Try to login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username, email, or password" in response.json()["detail"]

def test_protected_endpoint(client: TestClient):
    # Register and login a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "role": "PATIENT"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to access protected endpoint
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["role"] == "PATIENT"

def test_protected_endpoint_no_token(client: TestClient):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"] 