from pydantic import BaseModel, Field
from datetime import date

class JobseekerLoginRequestDto(BaseModel):
    email: str
    password: str

class JobseekerSignupRequestDto(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    birthdate: date
    gender: str
    address: str
    policy_agree_bool: bool = False
    
