from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import ALL models
from models.user import User
from models.property import Property, PropertyImage, Availability
from models.booking import Booking
from models.payment import Payment
from models.review import Review

# Import routers
from routers import auth, properties, bookings, payments

app = FastAPI(
    title="Vacation Rental Platform",
    description="A full-stack vacation rental booking platform like Airbnb",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register ALL routers
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(bookings.router)
app.include_router(payments.router)

@app.get("/")
def root():
    return {"message": "Vacation Rental API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}