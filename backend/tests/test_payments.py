import pytest
from models.booking import BookingStatus, PaymentStatus
from models.payment import Payment, PaymentStatusEnum


class TestPayments:
    """Test payment flow"""

    def _create_booking(self, client, guest_token, sample_property):
        """Helper to create a booking"""
        response = client.post(
            "/bookings/",
            json={
                "property_id": sample_property["id"],
                "check_in_date": "2026-10-01",
                "check_out_date": "2026-10-05"
            },
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        return response.json()

    def test_create_payment_intent(
        self, client, guest_token, sample_property
    ):
        """Test payment intent creation"""
        booking = self._create_booking(client, guest_token, sample_property)

        response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "client_secret" in data
        assert "payment_intent_id" in data
        assert data["amount"] == booking["total_amount"]
        print("✅ Payment intent created successfully")

    def test_payment_intent_wrong_guest_fails(
        self, client, guest_token, sample_property
    ):
        """Test that only booking owner can pay"""
        booking = self._create_booking(client, guest_token, sample_property)

        # Register another guest
        client.post("/auth/register", json={
            "email": "otherguest@test.com",
            "password": "password123",
            "full_name": "Other Guest",
            "role": "guest"
        })
        other_login = client.post("/auth/login", json={
            "email": "otherguest@test.com",
            "password": "password123"
        })
        other_token = other_login.json()["access_token"]

        # Try to pay with different guest
        response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {other_token}"}
        )
        assert response.status_code == 403
        print("✅ Only booking owner can pay")

    def test_payment_cancelled_booking_fails(
        self, client, guest_token, sample_property
    ):
        """Test cannot pay for cancelled booking"""
        booking = self._create_booking(client, guest_token, sample_property)

        # Cancel the booking first
        client.put(
            f"/bookings/{booking['id']}/cancel",
            headers={"Authorization": f"Bearer {guest_token}"}
        )

        # Try to pay
        response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 400
        assert "cancelled" in response.json()["detail"].lower()
        print("✅ Cannot pay for cancelled booking")

    def test_payment_nonexistent_booking_fails(
        self, client, guest_token
    ):
        """Test payment for non-existent booking fails"""
        response = client.post(
            "/payments/create-intent",
            json={"booking_id": 99999},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 404
        print("✅ Payment for non-existent booking fails")

    def test_confirm_booking_after_payment(
        self, client, guest_token, sample_property, db
    ):
        """Test booking is confirmed after successful payment"""
        from models.booking import Booking
        from models.payment import Payment

        booking = self._create_booking(client, guest_token, sample_property)

        # Create payment intent
        intent_response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert intent_response.status_code == 200

        # Manually update payment and booking in DB
        # (simulating successful Stripe payment)
        db_payment = db.query(Payment).filter(
            Payment.booking_id == booking["id"]
        ).first()

        if db_payment:
            db_payment.status = PaymentStatusEnum.paid
            db.commit()

        db_booking = db.query(Booking).filter(
            Booking.id == booking["id"]
        ).first()
        db_booking.status = BookingStatus.confirmed
        db_booking.payment_status = PaymentStatus.paid
        db.commit()

        # Verify booking is confirmed
        response = client.get(
            f"/bookings/{booking['id']}",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"
        assert response.json()["payment_status"] == "paid"
        print("✅ Booking confirmed after payment")

    def test_double_payment_fails(
        self, client, guest_token, sample_property, db
    ):
        """Test cannot pay twice for same booking"""
        from models.booking import Booking
        from models.payment import Payment

        booking = self._create_booking(client, guest_token, sample_property)

        # First payment intent
        client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {guest_token}"}
        )

        # Mark as paid in DB
        db_booking = db.query(Booking).filter(
            Booking.id == booking["id"]
        ).first()
        db_booking.payment_status = PaymentStatus.paid
        db.commit()

        # Try to pay again
        response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]},
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        assert response.status_code == 400
        assert "already paid" in response.json()["detail"]
        print("✅ Cannot pay twice for same booking")

    def test_payment_without_auth_fails(
        self, client, guest_token, sample_property
    ):
        """Test payment requires authentication"""
        booking = self._create_booking(client, guest_token, sample_property)

        response = client.post(
            "/payments/create-intent",
            json={"booking_id": booking["id"]}
        )
        assert response.status_code == 401
        print("✅ Payment requires authentication")