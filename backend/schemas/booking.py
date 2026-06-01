from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"
    completed = "completed"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


# Data needed to CREATE a booking
class BookingCreate(BaseModel):
    property_id: int
    check_in_date: date
    check_out_date: date

    @validator("check_out_date")
    def check_out_must_be_after_check_in(cls, check_out, values):
        if "check_in_date" in values and check_out <= values["check_in_date"]:
            raise ValueError("Check-out date must be after check-in date")
        return check_out


# What we RETURN for a booking
class BookingResponse(BaseModel):
    id: int
    property_id: int
    guest_id: int
    check_in_date: date
    check_out_date: date
    total_amount: float
    status: BookingStatus
    payment_status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Update booking status
class BookingStatusUpdate(BaseModel):
    status: BookingStatus