from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import date

from models.property import Property, PropertyImage, Availability
from models.booking import Booking, BookingStatus
from models.review import Review
from schemas.property import PropertyCreate, PropertyUpdate


def create_property(db: Session, property_data: PropertyCreate, host_id: int):
    new_property = Property(
        host_id=host_id,
        title=property_data.title,
        description=property_data.description,
        location=property_data.location,
        price_per_night=property_data.price_per_night,
        max_guests=property_data.max_guests
    )
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def get_property_by_id(db: Session, property_id: int):
    return db.query(Property).filter(Property.id == property_id).first()


def update_property(db: Session, property_id: int, property_data: PropertyUpdate, host_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    if property.host_id != host_id:
        raise HTTPException(status_code=403, detail="You can only update your own properties")
    update_data = property_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property, field, value)
    db.commit()
    db.refresh(property)
    return property


def delete_property(db: Session, property_id: int, host_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    if property.host_id != host_id:
        raise HTTPException(status_code=403, detail="You can only delete your own properties")
    db.delete(property)
    db.commit()
    return {"message": "Property deleted successfully"}


def add_property_image(db: Session, property_id: int, image_url: str, host_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    if property.host_id != host_id:
        raise HTTPException(status_code=403, detail="You can only add images to your own properties")
    new_image = PropertyImage(property_id=property_id, image_url=image_url)
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


def search_properties(
    db: Session,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    max_guests: Optional[int] = None,
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    page: int = 1,
    page_size: int = 10
):
    query = db.query(Property).options(joinedload(Property.images))

    if location:
        query = query.filter(Property.location.ilike(f"%{location}%"))

    if min_price is not None:
        query = query.filter(Property.price_per_night >= min_price)

    if max_price is not None:
        query = query.filter(Property.price_per_night <= max_price)

    if max_guests is not None:
        query = query.filter(Property.max_guests >= max_guests)

    if check_in and check_out:
        booked_property_ids = db.query(Booking.property_id).filter(
            Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
            Booking.check_in_date < check_out,
            Booking.check_out_date > check_in
        ).subquery()
        query = query.filter(Property.id.notin_(booked_property_ids))

    total = query.count()
    offset = (page - 1) * page_size
    properties = query.offset(offset).limit(page_size).all()

    return {
        "properties": properties,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


def set_availability(db: Session, property_id: int, available_date: date, is_available: bool, host_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    if property.host_id != host_id:
        raise HTTPException(status_code=403, detail="You can only manage your own properties")

    existing = db.query(Availability).filter(
        Availability.property_id == property_id,
        Availability.available_date == available_date
    ).first()

    if existing:
        existing.is_available = is_available
        db.commit()
        db.refresh(existing)
        return existing

    new_availability = Availability(
        property_id=property_id,
        available_date=available_date,
        is_available=is_available
    )
    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    return new_availability


def get_property_with_rating(db: Session, property_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    rating_result = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.property_id == property_id).first()

    avg_rating = round(float(rating_result[0]), 2) if rating_result[0] else None
    total_reviews = rating_result[1] or 0

    return {
        "id": property.id,
        "host_id": property.host_id,
        "title": property.title,
        "description": property.description,
        "location": property.location,
        "price_per_night": property.price_per_night,
        "max_guests": property.max_guests,
        "created_at": property.created_at,
        "images": property.images,
        "average_rating": avg_rating,
        "total_reviews": total_reviews
    }