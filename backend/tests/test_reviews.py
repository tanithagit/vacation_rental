import pytest
from models.booking import BookingStatus, PaymentStatus


class TestReviews:
    """Test review restrictions"""

    def _create_completed_booking(self, client, guest_token, sample_property, db):
        """Helper to create a completed booking"""
        from models.booking import Booking

        # Create booking
        booking = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-08-01",
                "check_out_date": "2026-08-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        ).json()

        # Mark as completed in DB
        db_booking = db.query(Booking).filter(
            Booking.id == booking["id"]
        ).first()
        db_booking.status = BookingStatus.completed
        db_booking.payment_status = PaymentStatus.paid
        db.commit()

        return booking

    def test_review_completed_booking(
        self, client, guest_token, sample_property, db
    ):
        """Test guest can review completed booking"""
        booking = self._create_completed_booking(
            client, guest_token, sample_property, db
        )
        response = client.post(
            "/reviews/",
            json={
                "booking_id": booking["id"],
                "rating": 5,
                "comment": "Amazing place!"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 201
        assert response.json()["rating"] == 5
        print("✅ Guest can review completed booking")

    def test_review_pending_booking_fails(
        self, client, guest_token, sample_property
    ):
        """Test cannot review pending booking"""
        booking = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-09-01",
                "check_out_date": "2026-09-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        ).json()

        response = client.post(
            "/reviews/",
            json={
                "booking_id": booking["id"],
                "rating": 5,
                "comment": "Great!"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 400
        assert "only review after" in response.json()["detail"].lower() or \
           "completed" in response.json()["detail"].lower()
        print("✅ Cannot review pending booking")

    def test_duplicate_review_fails(
        self, client, guest_token, sample_property, db
    ):
        """Test cannot submit two reviews for same booking"""
        booking = self._create_completed_booking(
            client, guest_token, sample_property, db
        )

        # First review
        client.post(
            "/reviews/",
            json={"booking_id": booking["id"], "rating": 5, "comment": "Great!"},
            headers={"Authorization": f"Bearer {guest_token}"}
        )

        # Second review - should fail
        response = client.post(
            "/reviews/",
            json={"booking_id": booking["id"], "rating": 3, "comment": "Ok"},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 400
        assert "already reviewed" in response.json()["detail"]
        print("✅ Duplicate review prevented")

    def test_invalid_rating_fails(
        self, client, guest_token, sample_property, db
    ):
        """Test rating must be between 1 and 5"""
        booking = self._create_completed_booking(
            client, guest_token, sample_property, db
        )
        response = client.post(
            "/reviews/",
            json={"booking_id": booking["id"], "rating": 6, "comment": "Test"},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 422
        print("✅ Invalid rating rejected")

    def test_get_property_reviews(
        self, client, guest_token, sample_property, db
    ):
        """Test getting all reviews for a property"""
        booking = self._create_completed_booking(
            client, guest_token, sample_property, db
        )
        client.post(
            "/reviews/",
            json={"booking_id": booking["id"], "rating": 4, "comment": "Good!"},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        response = client.get(f"/reviews/property/{sample_property['id']}")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "reviews" in data
        assert data["summary"]["total_reviews"] >= 1
        print("✅ Property reviews retrieved successfully")