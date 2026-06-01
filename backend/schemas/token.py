from pydantic import BaseModel
from typing import Optional

# What we return after successful login
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str

# Data stored INSIDE the JWT token
class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None