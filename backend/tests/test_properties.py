import pytest


class TestProperties:
    """Test property listing and search"""

    def test_create_property_as_host(self, client, host_token):
        """Test host can create property"""
        response = client.post(
            "/properties/",
            json={
                "title": "Beach House",
                "description": "Nice beach house",
                "location": "Chennai",
                "price_per_night": 2500.0,
                "max_guests": 4
            },
            headers={"Authorization": f"Bearer {host_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Beach House"
        assert data["location"] == "Chennai"
        print("✅ Host can create property")

    def test_create_property_as_guest_fails(self, client, guest_token):
        """Test guest cannot create property"""
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
        print("✅ Guest cannot create property")

    def test_search_by_location(self, client, sample_property):
        """Test search by location works"""
        response = client.get("/properties/search?location=Chennai")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for prop in data["properties"]:
            assert "chennai" in prop["location"].lower()
        print("✅ Search by location works")

    def test_search_by_price_range(self, client, sample_property):
        """Test filter by price range"""
        response = client.get(
            "/properties/search?min_price=1000&max_price=3000"
        )
        assert response.status_code == 200
        data = response.json()
        for prop in data["properties"]:
            assert prop["price_per_night"] >= 1000
            assert prop["price_per_night"] <= 3000
        print("✅ Price range filter works")

    def test_search_by_guest_count(self, client, sample_property):
        """Test filter by guest count"""
        response = client.get("/properties/search?max_guests=4")
        assert response.status_code == 200
        data = response.json()
        for prop in data["properties"]:
            assert prop["max_guests"] >= 4
        print("✅ Guest count filter works")

    def test_search_pagination(self, client, sample_property):
        """Test pagination works"""
        response = client.get(
            "/properties/search?page=1&page_size=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "total_pages" in data
        assert len(data["properties"]) <= 5
        print("✅ Pagination works")

    def test_get_property_by_id(self, client, sample_property):
        """Test getting single property"""
        property_id = sample_property["id"]
        response = client.get(f"/properties/{property_id}")
        assert response.status_code == 200
        assert response.json()["id"] == property_id
        print("✅ Get property by ID works")

    def test_update_property_by_owner(self, client, host_token, sample_property):
        """Test host can update own property"""
        property_id = sample_property["id"]
        response = client.put(
            f"/properties/{property_id}",
            json={"title": "Updated Beach House"},
            headers={"Authorization": f"Bearer {host_token}"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Beach House"
        print("✅ Host can update own property")

    def test_delete_property_by_owner(self, client, host_token, sample_property):
        """Test host can delete own property"""
        property_id = sample_property["id"]
        response = client.delete(
            f"/properties/{property_id}",
            headers={"Authorization": f"Bearer {host_token}"}
        )
        assert response.status_code == 200
        print("✅ Host can delete own property")