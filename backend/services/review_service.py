from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional

from models.review import Review
from models.booking import Booking, BookingStatus
from models.property import Property
from models.user import User
from schemas.review import ReviewCreate


def create_review(
    db: Session,
    review_data: ReviewCreate,
    guest_id: int
) -> dict:
    """
    Create a review with all restrictions:
    1. Only completed bookings can be reviewed
    2. One review per booking
    3. Cannot review own property
    """

    # Get the booking
    booking = db.query(Booking).filter(
        Booking.id == review_data.booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Rule 1: Only the guest who made the booking can review
    if booking.guest_id != guest_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own bookings"
        )

    # Rule 2: Only COMPLETED bookings can be reviewed
    if booking.status != BookingStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review after completing your stay"
        )

    # Rule 3: One review per booking
    existing_review = db.query(Review).filter(
        Review.booking_id == review_data.booking_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this booking"
        )

    # Rule 4: Cannot review own property
    property = db.query(Property).filter(
        Property.id == booking.property_id
    ).first()

    if property.host_id == guest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot review your own property"
        )

    # Create the review
    new_review = Review(
        property_id=booking.property_id,
        guest_id=guest_id,
        booking_id=review_data.booking_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Get guest name to return
    guest = db.query(User).filter(User.id == guest_id).first()

    return {
        "id": new_review.id,
        "property_id": new_review.property_id,
        "guest_id": new_review.guest_id,
        "booking_id": new_review.booking_id,
        "rating": new_review.rating,
        "comment": new_review.comment,
        "created_at": new_review.created_at,
        "guest_name": guest.full_name if guest else None
    }


def get_property_reviews(
    db: Session,
    property_id: int
) -> List[dict]:
    """Get all reviews for a property with guest names"""

    reviews = db.query(Review).filter(
        Review.property_id == property_id
    ).order_by(Review.created_at.desc()).all()

    result = []
    for review in reviews:
        guest = db.query(User).filter(User.id == review.guest_id).first()
        result.append({
            "id": review.id,
            "property_id": review.property_id,
            "guest_id": review.guest_id,
            "booking_id": review.booking_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "guest_name": guest.full_name if guest else None
        })

    return result


def get_property_rating_summary(
    db: Session,
    property_id: int
) -> dict:
    """Get average rating and total reviews for a property"""

    result = db.query(
        func.avg(Review.rating).label("average"),
        func.count(Review.id).label("total")
    ).filter(Review.property_id == property_id).first()

    return {
        "average_rating": round(float(result.average), 2) if result.average else None,
        "total_reviews": result.total or 0
    }


def delete_review(
    db: Session,
    review_id: int,
    guest_id: int
) -> dict:
    """Delete a review - only the author can delete"""

    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.guest_id != guest_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}


def get_guest_reviews(
    db: Session,
    guest_id: int
) -> List[dict]:
    """Get all reviews written by a guest"""

    reviews = db.query(Review).filter(
        Review.guest_id == guest_id
    ).order_by(Review.created_at.desc()).all()

    result = []
    for review in reviews:
        property = db.query(Property).filter(
            Property.id == review.property_id
        ).first()
        result.append({
            "id": review.id,
            "property_id": review.property_id,
            "property_title": property.title if property else None,
            "guest_id": review.guest_id,
            "booking_id": review.booking_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        })

    return result