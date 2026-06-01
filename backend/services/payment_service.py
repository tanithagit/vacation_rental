import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from config import settings
from models.payment import Payment, PaymentStatusEnum
from models.booking import Booking, BookingStatus, PaymentStatus
from models.user import User
from services.booking_service import get_booking_by_id, confirm_booking
from services.email_service import (
    send_booking_confirmation_email,
    send_payment_confirmation_email,
    send_host_booking_notification
)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(db: Session, booking_id: int, guest_id: int) -> dict:
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.guest_id != guest_id:
        raise HTTPException(status_code=403, detail="You can only pay for your own bookings")

    if booking.status == BookingStatus.canceled:
        raise HTTPException(status_code=400, detail="Cannot pay for a cancelled booking")

    if booking.payment_status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="This booking is already paid")

    amount_in_paise = int(booking.total_amount * 100)

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency="inr",
            metadata={
                "booking_id": booking_id,
                "guest_id": guest_id
            }
        )

        payment_record = Payment(
            booking_id=booking_id,
            stripe_payment_intent_id=payment_intent.id,
            amount=booking.total_amount,
            status=PaymentStatusEnum.pending
        )
        db.add(payment_record)
        db.commit()

        return {
            "client_secret": payment_intent.client_secret,
            "payment_intent_id": payment_intent.id,
            "amount": booking.total_amount,
            "currency": "inr"
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")


def confirm_payment(db: Session, payment_intent_id: str, guest_id: int) -> dict:
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")

    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_intent.status == "succeeded":
            payment.status = PaymentStatusEnum.paid
            db.commit()

            booking = confirm_booking(db, payment.booking_id)

            guest = db.query(User).filter(User.id == booking.guest_id).first()
            property = booking.property
            host = db.query(User).filter(User.id == property.host_id).first()

            send_booking_confirmation_email(
                guest_email=guest.email,
                guest_name=guest.full_name,
                property_title=property.title,
                check_in=str(booking.check_in_date),
                check_out=str(booking.check_out_date),
                total_amount=booking.total_amount
            )

            send_payment_confirmation_email(
                guest_email=guest.email,
                guest_name=guest.full_name,
                amount=booking.total_amount,
                property_title=property.title
            )

            send_host_booking_notification(
                host_email=host.email,
                host_name=host.full_name,
                guest_name=guest.full_name,
                property_title=property.title,
                check_in=str(booking.check_in_date),
                check_out=str(booking.check_out_date),
                total_amount=booking.total_amount
            )

            return {
                "message": "Payment confirmed successfully",
                "booking_id": booking.id,
                "booking_status": booking.status,
                "payment_status": payment.status
            }

        else:
            payment.status = PaymentStatusEnum.failed
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Payment not successful. Status: {payment_intent.status}"
            )

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")