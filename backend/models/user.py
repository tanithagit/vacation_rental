from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

# These are the allowed roles in our system
class UserRole(str, enum.Enum):
    host = "host"
    guest = "guest"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.guest, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships - connects to other tables
    properties = relationship("Property", back_populates="host")
    bookings = relationship("Booking", back_populates="guest")
    reviews = relationship("Review", back_populates="guest")