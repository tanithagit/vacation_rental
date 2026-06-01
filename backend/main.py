from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import ALL models first - this is critical!
from models.user import User
from models.property import Property, PropertyImage, Availability
from models.booking import Booking
from models.payment import Payment
from models.review import Review

# Import routers
from routers import auth

app = FastAPI(
    title="Vacation Rental Platform",
    description="A full-stack vacation rental booking platform like Airbnb",
    version="1.0.0"
)

# CORS allows React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Vacation Rental API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}