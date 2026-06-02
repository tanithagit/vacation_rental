import pytest


class TestAuthentication:
    """Test all authentication flows"""

    def test_register_guest_success(self, client):
        """Test successful guest registration"""
        response = client.post("/auth/register", json={
            "email": "newguest@test.com",
            "password": "password123",
            "full_name": "New Guest",
            "role": "guest"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newguest@test.com"
        assert data["role"] == "guest"
        assert "hashed_password" not in data
        print("✅ Guest registration works")

    def test_register_host_success(self, client):
        """Test successful host registration"""
        response = client.post("/auth/register", json={
            "email": "newhost@test.com",
            "password": "password123",
            "full_name": "New Host",
            "role": "host"
        })
        assert response.status_code == 201
        assert response.json()["role"] == "host"
        print("✅ Host registration works")

    def test_register_duplicate_email(self, client):
        """Test that duplicate email is rejected"""
        client.post("/auth/register", json={
            "email": "duplicate@test.com",
            "password": "password123",
            "full_name": "User One",
            "role": "guest"
        })
        # Try registering with same email
        response = client.post("/auth/register", json={
            "email": "duplicate@test.com",
            "password": "password456",
            "full_name": "User Two",
            "role": "guest"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
        print("✅ Duplicate email rejected")

    def test_login_success(self, client):
        """Test successful login returns token"""
        client.post("/auth/register", json={
            "email": "logintest@test.com",
            "password": "password123",
            "full_name": "Login Test",
            "role": "guest"
        })
        response = client.post("/auth/login", json={
            "email": "logintest@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print("✅ Login returns JWT token")

    def test_login_wrong_password(self, client):
        """Test login with wrong password fails"""
        client.post("/auth/register", json={
            "email": "wrongpass@test.com",
            "password": "password123",
            "full_name": "Wrong Pass",
            "role": "guest"
        })
        response = client.post("/auth/login", json={
            "email": "wrongpass@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✅ Wrong password rejected")

    def test_get_profile_with_token(self, client, guest_token):
        """Test getting profile with valid token"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 200
        assert "email" in response.json()
        print("✅ Profile accessible with token")

    def test_get_profile_without_token(self, client):
        """Test that protected route requires token"""
        response = client.get("/auth/me")
        assert response.status_code == 401
        print("✅ Protected route requires token")

    def test_role_based_access_host_only(self, client, guest_token):
        """Test that guest cannot access host routes"""
        response = client.post(
            "/properties/",
            json={
                "title": "Test Property",
                "description": "Test",
                "location": "Chennai",
                "price_per_night": 1000.0,
                "max_guests": 2
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 403
        print("✅ Guest cannot create property (host only)")