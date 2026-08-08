from pydantic import BaseModel, Field


class HospitalCreateRequest(BaseModel):
    name: str = Field(..., description="Hospital name.")
    address: str = Field(..., description="Hospital address.")
    phone: str = Field(..., description="Hospital phone number.")
    owner_first_name: str = Field(..., description="Owner's first name.")
    owner_last_name: str = Field(..., description="Owner's last name.")
    owner_email: str = Field(..., description="Owner's email address.")
    owner_password: str = Field(..., description="Owner's password.", min_length=8)


class AddDoctorRequest(BaseModel):
    first_name: str = Field(..., description="Doctor's first name.")
    last_name: str = Field(..., description="Doctor's last name.")
    email: str = Field(..., description="Doctor's email address.")
    password: str = Field(..., description="Doctor's password.", min_length=8)
