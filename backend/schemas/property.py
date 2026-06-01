from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# Data needed to CREATE a property
class PropertyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price_per_night: float
    max_guests: int


# Data needed to UPDATE a property
class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    price_per_night: Optional[float] = None
    max_guests: Optional[int] = None


# Image response
class PropertyImageResponse(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True


# What we RETURN for a property
class PropertyResponse(BaseModel):
    id: int
    host_id: int
    title: str
    description: Optional[str] = None
    location: str
    price_per_night: float
    max_guests: int
    created_at: datetime
    images: List[PropertyImageResponse] = []

    class Config:
        from_attributes = True


# Property with average rating
class PropertyWithRating(BaseModel):
    id: int
    host_id: int
    title: str
    description: Optional[str] = None
    location: str
    price_per_night: float
    max_guests: int
    created_at: datetime
    images: List[PropertyImageResponse] = []
    average_rating: Optional[float] = None
    total_reviews: int = 0

    class Config:
        from_attributes = True


# Availability schema
class AvailabilityCreate(BaseModel):
    available_date: date
    is_available: bool = True


class AvailabilityResponse(BaseModel):
    id: int
    property_id: int
    available_date: date
    is_available: bool

    class Config:
        from_attributes = True