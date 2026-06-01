from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String, nullable=False, index=True)
    price_per_night = Column(Float, nullable=False)
    max_guests = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    host = relationship("User", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property")
    bookings = relationship("Booking", back_populates="property")
    reviews = relationship("Review", back_populates="property")
    availability = relationship("Availability", back_populates="property")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    image_url = Column(String, nullable=False)

    property = relationship("Property", back_populates="images")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    available_date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True)

    property = relationship("Property", back_populates="availability")