from pydantic import BaseModel, EmailStr, Field


class UserSignUpRequest(BaseModel):
    first_name: str = Field(..., description="The user's first name.")
    last_name: str = Field(..., description="The user's last name.")
    email: EmailStr = Field(..., description="The user's email address.")
    password: str = Field(..., description="The user's password.", min_length=8)


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="The user's email address.",
    )
    password: str = Field(
        ...,
        description="The user's password.",
        min_length=8,
    )