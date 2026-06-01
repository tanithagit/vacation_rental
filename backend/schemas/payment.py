from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentStatusEnum(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class PaymentIntentCreate(BaseModel):
    booking_id: int


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str = "inr"


class PaymentConfirm(BaseModel):
    payment_intent_id: str


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    stripe_payment_intent_id: str
    amount: float
    status: PaymentStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True