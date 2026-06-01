from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.booking import BookingCreate, BookingResponse
from services.auth_service import get_current_user, get_current_guest
from services.booking_service import (
    create_booking,
    get_booking_by_id,
    get_guest_bookings,
    get_host_bookings,
    cancel_booking,
    get_upcoming_bookings_for_host,
    get_host_revenue
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
def create_new_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new booking.
    Checks:
    - Property exists
    - No double booking
    - Check-out after check-in
    - Guest not booking own property
    """
    return create_booking(db, booking_data, current_user.id)


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for the logged in guest"""
    return get_guest_bookings(db, current_user.id)


@router.get("/host-bookings", response_model=List[BookingResponse])
def get_bookings_for_host(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for host's properties"""
    return get_host_bookings(db, current_user.id)


@router.get("/host-dashboard")
def get_host_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Host dashboard data:
    - Total bookings
    - Total revenue
    - Upcoming stays
    """
    all_bookings = get_host_bookings(db, current_user.id)
    upcoming = get_upcoming_bookings_for_host(db, current_user.id)
    revenue = get_host_revenue(db, current_user.id)

    return {
        "total_bookings": len(all_bookings),
        "total_revenue": revenue,
        "upcoming_stays": len(upcoming),
        "upcoming_bookings": upcoming
    }


@router.get("/{booking_id}", response_model=BookingResponse)
def get_single_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single booking by ID"""
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    # Only the guest or host can see this booking
    if booking.guest_id != current_user.id:
        property = booking.property
        if property.host_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this booking"
            )
    return booking


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_existing_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking"""
    return cancel_booking(db, booking_id, current_user.id)