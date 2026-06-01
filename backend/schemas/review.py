from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    booking_id: int
    rating: int
    comment: Optional[str] = None

    @validator("rating")
    def rating_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    property_id: int
    guest_id: int
    booking_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    guest_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

    @validator("rating")
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v