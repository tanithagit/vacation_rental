from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from schemas.review import ReviewCreate, ReviewResponse
from services.auth_service import get_current_user
from services.review_service import (
    create_review,
    get_property_reviews,
    get_property_rating_summary,
    delete_review,
    get_guest_reviews
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", status_code=201)
def submit_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a review for a completed stay.
    Rules:
    - Only completed bookings
    - One review per booking
    - Cannot review own property
    """
    return create_review(db, review_data, current_user.id)


@router.get("/property/{property_id}")
def get_reviews_for_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Get all reviews for a property - PUBLIC"""
    reviews = get_property_reviews(db, property_id)
    summary = get_property_rating_summary(db, property_id)
    return {
        "summary": summary,
        "reviews": reviews
    }


@router.get("/my-reviews")
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews written by logged in guest"""
    return get_guest_reviews(db, current_user.id)


@router.delete("/{review_id}")
def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review - only author can delete"""
    return delete_review(db, review_id, current_user.id)