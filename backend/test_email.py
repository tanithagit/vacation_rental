import sys
sys.path.append(".")

from services.email_service import send_booking_confirmation_email

print("Sending test email...")

send_booking_confirmation_email(
    guest_email="guest@test.com",
    guest_name="Test Guest",
    property_title="Beautiful Beach House",
    check_in="2026-09-01",
    check_out="2026-09-03",
    total_amount=9000.0
)

print("Email sent successfully!")