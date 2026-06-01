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
    """
    Check if there are any overlapping bookings.
    Returns True if there IS a conflict (dates are taken)
    """
    query = db.query(Booking).filter(
        Booking.property_id == property_id,
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        # Overlap condition:
        # Existing booking starts before our checkout
        # AND existing booking ends after our checkin
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    )

    # Exclude current booking when updating
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.first() is not None


def calculate_total_amount(
    price_per_night: float,
    check_in: date,
    check_out: date
) -> float:
    """Calculate total booking amount"""
    num_nights = (check_out - check_in).days
    return price_per_night * num_nights


def create_booking(
    db: Session,
    booking_data: BookingCreate,
    guest_id: int
) -> Booking:
    """
    Create a new booking with all validation checks
    This implements all the critical booking rules
    """

    # Rule 1: Check property exists
    property = db.query(Property).filter(
        Property.id == booking_data.property_id
    ).first()

    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )

    # Rule 2: Prevent host from booking their own property
    if property.host_id == guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot book your own property"
        )

    # Rule 3: Validate check-out is after check-in
    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )

    # Rule 4: Check-in must be in the future
    if booking_data.check_in_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past"
        )

    # Rule 5: Check for overlapping bookings (prevent double booking)
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

    # Calculate total amount
    total_amount = calculate_total_amount(
        price_per_night=property.price_per_night,
        check_in=booking_data.check_in_date,
        check_out=booking_data.check_out_date
    )

    # Create the booking with PENDING status
    # Status becomes CONFIRMED only after payment
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
    """Get a single booking by ID"""
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_guest_bookings(db: Session, guest_id: int) -> List[Booking]:
    """Get all bookings for a guest"""
    return db.query(Booking).filter(
        Booking.guest_id == guest_id
    ).order_by(Booking.created_at.desc()).all()


def get_host_bookings(db: Session, host_id: int) -> List[Booking]:
    """Get all bookings for properties owned by a host"""
    return db.query(Booking).join(Property).filter(
        Property.host_id == host_id
    ).order_by(Booking.created_at.desc()).all()


def cancel_booking(
    db: Session,
    booking_id: int,
    user_id: int
) -> Booking:
    """Cancel a booking"""
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Only the guest who made the booking can cancel it
    if booking.guest_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )

    # Cannot cancel already completed or canceled bookings
    if booking.status in [BookingStatus.completed, BookingStatus.canceled]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a {booking.status} booking"
        )

    booking.status = BookingStatus.canceled
    db.commit()
    db.refresh(booking)
    return booking


def confirm_booking(db: Session, booking_id: int) -> Booking:
    """
    Confirm a booking after successful payment
    This is called automatically after payment succeeds
    """
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
    return booking


def complete_booking(db: Session, booking_id: int) -> Booking:
    """Mark a booking as completed after stay ends"""
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


def get_upcoming_bookings_for_host(
    db: Session,
    host_id: int
) -> List[Booking]:
    """Get upcoming bookings for host dashboard"""
    today = date.today()
    return db.query(Booking).join(Property).filter(
        Property.host_id == host_id,
        Booking.check_in_date >= today,
        Booking.status == BookingStatus.confirmed
    ).order_by(Booking.check_in_date).all()


def get_host_revenue(db: Session, host_id: int) -> float:
    """Calculate total revenue for a host"""
    bookings = db.query(Booking).join(Property).filter(
        Property.host_id == host_id,
        Booking.payment_status == PaymentStatus.paid
    ).all()

    return sum(b.total_amount for b in bookings)