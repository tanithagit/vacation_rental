from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, datetime
from typing import List, Optional

from models.booking import Booking, BookingStatus, PaymentStatus
from models.property import Property
from models.user import User
from schemas.booking import BookingCreate


def check_booking_conflicts(
    db: Session,
    property_id: int,
    check_in: date,
    check_out: date,
    exclude_booking_id: Optional[int] = None
) -> bool:
    query = db.query(Booking).filter(
        Booking.property_id == property_id,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    )
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    return query.first() is not None


def calculate_total_amount(
    price_per_night: float,
    check_in: date,
    check_out: date
) -> float:
    num_nights = (check_out - check_in).days
    return price_per_night * num_nights


def create_booking(
    db: Session,
    booking_data: BookingCreate,
    guest_id: int
) -> Booking:
    # Rule 1: Check property exists
    property = db.query(Property).filter(
        Property.id == booking_data.property_id
    ).first()

    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )

    # Rule 2: Prevent host booking own property
    if property.host_id == guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot book your own property"
        )

    # Rule 3: Validate dates
    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )

    # Rule 4: Check-in must be future
    if booking_data.check_in_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past"
        )

    # Rule 5: Check double booking
    has_conflict = check_booking_conflicts(
        db=db,
        property_id=booking_data.property_id,
        check_in=booking_data.check_in_date,
        check_out=booking_data.check_out_date
    )

    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Property is not available for the selected dates"
        )

    # Calculate total
    total_amount = calculate_total_amount(
        price_per_night=property.price_per_night,
        check_in=booking_data.check_in_date,
        check_out=booking_data.check_out_date
    )

    # Create booking
    new_booking = Booking(
        property_id=booking_data.property_id,
        guest_id=guest_id,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        total_amount=total_amount,
        status=BookingStatus.pending,
        payment_status=PaymentStatus.pending
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_guest_bookings(db: Session, guest_id: int) -> List[Booking]:
    return db.query(Booking).filter(
        Booking.guest_id == guest_id
    ).order_by(Booking.created_at.desc()).all()


def get_host_bookings(db: Session, host_id: int) -> List[Booking]:
    return db.query(Booking).join(Property).filter(
        Property.host_id == host_id
    ).order_by(Booking.created_at.desc()).all()


def cancel_booking(db: Session, booking_id: int, user_id: int) -> Booking:
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.guest_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )

    if booking.status in [BookingStatus.completed, BookingStatus.canceled]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a {booking.status} booking"
        )

    booking.status = BookingStatus.canceled
    db.commit()
    db.refresh(booking)

    # Send cancellation email
    try:
        from services.email_service import send_booking_cancellation_email
        guest = db.query(User).filter(User.id == booking.guest_id).first()
        property = db.query(Property).filter(
            Property.id == booking.property_id
        ).first()

        if guest and property:
            send_booking_cancellation_email(
                guest_email=guest.email,
                guest_name=guest.full_name,
                property_title=property.title,
                check_in=str(booking.check_in_date),
                check_out=str(booking.check_out_date)
            )
    except Exception as e:
        print(f"Email sending failed: {e}")

    return booking


def confirm_booking(db: Session, booking_id: int) -> Booking:
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    booking.status = BookingStatus.confirmed
    booking.payment_status = PaymentStatus.paid
    db.commit()
    db.refresh(booking)

    # Send confirmation emails
    try:
        from services.email_service import (
            send_booking_confirmation_email,
            send_payment_confirmation_email,
            send_host_booking_notification
        )

        guest = db.query(User).filter(User.id == booking.guest_id).first()
        property = db.query(Property).filter(
            Property.id == booking.property_id
        ).first()
        host = db.query(User).filter(User.id == property.host_id).first()

        if guest and property:
            # Email to guest
            send_booking_confirmation_email(
                guest_email=guest.email,
                guest_name=guest.full_name,
                property_title=property.title,
                check_in=str(booking.check_in_date),
                check_out=str(booking.check_out_date),
                total_amount=booking.total_amount
            )

            # Payment receipt to guest
            send_payment_confirmation_email(
                guest_email=guest.email,
                guest_name=guest.full_name,
                amount=booking.total_amount,
                property_title=property.title
            )

        if host and property:
            # Notify host
            send_host_booking_notification(
                host_email=host.email,
                host_name=host.full_name,
                guest_name=guest.full_name if guest else "Guest",
                property_title=property.title,
                check_in=str(booking.check_in_date),
                check_out=str(booking.check_out_date),
                total_amount=booking.total_amount
            )
    except Exception as e:
        print(f"Email sending failed: {e}")

    return booking


def complete_booking(db: Session, booking_id: int) -> Booking:
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != BookingStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed bookings can be completed"
        )

    booking.status = BookingStatus.completed
    db.commit()
    db.refresh(booking)
    return booking


def get_upcoming_bookings_for_host(db: Session, host_id: int) -> List[Booking]:
    today = date.today()
    return db.query(Booking).join(Property).filter(
        Property.host_id == host_id,
        Booking.check_in_date >= today,
        Booking.status == BookingStatus.confirmed
    ).order_by(Booking.check_in_date).all()


def get_host_revenue(db: Session, host_id: int) -> float:
    bookings = db.query(Booking).join(Property).filter(
        Property.host_id == host_id,
        Booking.payment_status == PaymentStatus.paid
    ).all()
    return sum(b.total_amount for b in bookings)