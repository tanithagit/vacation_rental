from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional

class UserRole(str, Enum):
    host = "host"
    guest = "guest"
    admin = "admin"

# Data needed to REGISTER a new user
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.guest

# Data needed to LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Data we RETURN about a user (never return password!)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

# Data to UPDATE user profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None