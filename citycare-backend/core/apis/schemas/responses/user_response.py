from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    status: str
    created_at: datetime


class UserLoginResponse(BaseModel):
    access_token: str
    role: str
