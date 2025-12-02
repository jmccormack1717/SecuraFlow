"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.database.models import User
from app.utils.auth import get_password_hash


def test_signup_success(client):
    """Test successful user signup."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data  # Password should not be in response


def test_signup_duplicate_email(client):
    """Test signup with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "password123"
    }
    # Create first user
    client.post("/api/auth/signup", json=user_data)
    
    # Try to create second user with same email
    user_data["username"] = "user2"
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


def test_signup_duplicate_username(client):
    """Test signup with duplicate username."""
    user_data = {
        "email": "user1@example.com",
        "username": "duplicate",
        "password": "password123"
    }
    # Create first user
    client.post("/api/auth/signup", json=user_data)
    
    # Try to create second user with same username
    user_data["email"] = "user2@example.com"
    response = client.post("/api/auth/signup", json=user_data)
    assert response.status_code == 400
    assert "username already taken" in response.json()["detail"].lower()


def test_signup_invalid_data(client):
    """Test signup with invalid data."""
    # Missing required fields
    response = client.post("/api/auth/signup", json={"email": "test@example.com"})
    assert response.status_code == 422
    
    # Invalid email format
    response = client.post("/api/auth/signup", json={
        "email": "invalid-email",
        "username": "test",
        "password": "password123"
    })
    assert response.status_code == 422


def test_login_success(client, db_session):
    """Test successful login."""
    # Create a user first
    user = User(
        email="login@example.com",
        username="loginuser",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_username(client):
    """Test login with invalid username."""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "password123"}
    )
    assert response.status_code == 401
    assert "incorrect username or password" in response.json()["detail"].lower()


def test_login_invalid_password(client, db_session):
    """Test login with invalid password."""
    # Create a user first
    user = User(
        email="login2@example.com",
        username="loginuser2",
        hashed_password=get_password_hash("correctpassword")
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser2", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "incorrect username or password" in response.json()["detail"].lower()


def test_login_inactive_user(client, db_session):
    """Test login with inactive user account."""
    # Create an inactive user
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password=get_password_hash("password123"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to login
    response = client.post(
        "/api/auth/login",
        data={"username": "inactiveuser", "password": "password123"}
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_demo_login(client):
    """Test demo login endpoint."""
    response = client.post("/api/auth/demo")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user_with_token(client, db_session):
    """Test getting current user with valid token."""
    # Create a user and get token
    user = User(
        email="current@example.com",
        username="currentuser",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "currentuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # FastAPI OAuth2 returns 403 for missing token


def test_get_current_user_demo_token(client):
    """Test getting current user with demo token."""
    # Get demo token
    demo_response = client.post("/api/auth/demo")
    token = demo_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "demo_user"
    assert data["email"] == "demo@securaflow.com"

