from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.payment import PaymentIntentCreate, PaymentIntentResponse, PaymentConfirm
from services.auth_service import get_current_user
from services.payment_service import create_payment_intent, confirm_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-intent")
def create_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 1 of payment:
    Create a Stripe Payment Intent for a booking.
    Returns client_secret for frontend to complete payment.
    """
    return create_payment_intent(db, payment_data.booking_id, current_user.id)


@router.post("/confirm")
def confirm_payment_route(
    payment_data: PaymentConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 2 of payment:
    Confirm payment after Stripe payment succeeds.
    Updates booking to CONFIRMED and sends emails.
    """
    return confirm_payment(db, payment_data.payment_intent_id, current_user.id)