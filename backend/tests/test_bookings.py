import pytest


class TestBookings:
    """Test all booking rules and conflict prevention"""

    def test_create_booking_success(self, client, guest_token, sample_property):
        """Test successful booking creation"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-10-01",
                "check_out_date": "2026-10-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["total_amount"] == 10000.0
        print("✅ Booking created successfully")

    def test_double_booking_prevention(self, client, guest_token, sample_property):
        """Test that double booking is prevented"""
        # First booking
        client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-11-01",
                "check_out_date": "2026-11-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        # Try to book same dates again
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-11-02",
                "check_out_date": "2026-11-06"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 409
        assert "not available" in response.json()["detail"]
        print("✅ Double booking prevented")

    def test_checkout_before_checkin_fails(self, client, guest_token, sample_property):
        """Test that check-out before check-in is rejected"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-10-10",
                "check_out_date": "2026-10-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code in [400, 422]
        print("✅ Check-out before check-in rejected")

    def test_past_date_booking_fails(self, client, guest_token, sample_property):
        """Test that past date booking is rejected"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2020-01-01",
                "check_out_date": "2020-01-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 400
        assert "past" in response.json()["detail"]
        print("✅ Past date booking rejected")

    def test_host_cannot_book_own_property(
        self, client, host_token, sample_property
    ):
        """Test that host cannot book their own property"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-12-01",
                "check_out_date": "2026-12-05"
            },
            headers={"Authorization": f"Bearer {host_token}"}
        )
        assert response.status_code == 400
        assert "own property" in response.json()["detail"]
        print("✅ Host cannot book own property")

    def test_cancel_booking(self, client, guest_token, sample_property):
        """Test booking cancellation"""
        # Create booking
        booking = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-12-10",
                "check_out_date": "2026-12-15"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        ).json()

        # Cancel it
        response = client.put(
            f"/bookings/{booking['id']}/cancel",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "canceled"
        print("✅ Booking cancellation works")

    def test_total_amount_calculation(
        self, client, guest_token, sample_property
    ):
        """Test total amount is correctly calculated"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-10-20",
                "check_out_date": "2026-10-25"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 201
        # 5 nights × 2500 = 12500
        assert response.json()["total_amount"] == 12500.0
        print("✅ Total amount calculated correctly")