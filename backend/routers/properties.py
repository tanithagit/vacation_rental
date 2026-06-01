from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from database import get_db
from models.user import User
from schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyWithRating,
    AvailabilityCreate,
    AvailabilityResponse
)
from services.auth_service import get_current_user, get_current_host
from services.property_service import (
    create_property,
    get_property_by_id,
    update_property,
    delete_property,
    add_property_image,
    search_properties,
    set_availability,
    get_property_with_rating
)

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", response_model=PropertyResponse, status_code=201)
def create_new_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Create a new property - HOSTS ONLY"""
    return create_property(db, property_data, current_user.id)


@router.get("/search")
def search_available_properties(
    location: Optional[str] = Query(None, description="Search by city or area"),
    min_price: Optional[float] = Query(None, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, description="Maximum price per night"),
    max_guests: Optional[int] = Query(None, description="Number of guests"),
    check_in: Optional[date] = Query(None, description="Check-in date YYYY-MM-DD"),
    check_out: Optional[date] = Query(None, description="Check-out date YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Results per page")
):
    """Search and filter properties - PUBLIC (no login needed)"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Validate dates if provided
        if check_in and check_out:
            if check_out <= check_in:
                raise HTTPException(
                    status_code=400,
                    detail="Check-out date must be after check-in date"
                )
        return search_properties(
            db=db,
            location=location,
            min_price=min_price,
            max_price=max_price,
            max_guests=max_guests,
            check_in=check_in,
            check_out=check_out,
            page=page,
            page_size=page_size
        )
    finally:
        db.close()


@router.get("/{property_id}", response_model=PropertyWithRating)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Get a single property with rating - PUBLIC"""
    return get_property_with_rating(db, property_id)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_existing_property(
    property_id: int,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Update a property - HOSTS ONLY"""
    return update_property(db, property_id, property_data, current_user.id)


@router.delete("/{property_id}")
def delete_existing_property(
    property_id: int,
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Delete a property - HOSTS ONLY"""
    return delete_property(db, property_id, current_user.id)


@router.post("/{property_id}/images", status_code=201)
def upload_property_image(
    property_id: int,
    image_url: str = Query(..., description="URL of the image"),
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Add image to property - HOSTS ONLY"""
    return add_property_image(db, property_id, image_url, current_user.id)


@router.post("/{property_id}/availability", response_model=AvailabilityResponse)
def set_property_availability(
    property_id: int,
    availability_data: AvailabilityCreate,
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Set availability for a date - HOSTS ONLY"""
    return set_availability(
        db,
        property_id,
        availability_data.available_date,
        availability_data.is_available,
        current_user.id
    )


@router.get("/host/my-properties", response_model=List[PropertyResponse])
def get_my_properties(
    current_user: User = Depends(get_current_host),
    db: Session = Depends(get_db)
):
    """Get all properties owned by logged in host"""
    from models.property import Property
    return db.query(Property).filter(
        Property.host_id == current_user.id
    ).all()