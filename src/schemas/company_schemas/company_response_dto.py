from pydantic import BaseModel
from typing import Optional

class CompanyResponseDto(BaseModel):
    company_id: int
    email: str
    name: str
    user_type: str = "company"

class CompanyLoginResponseDto(BaseModel):
    message: str
    company_id: int
    name: str
    email: str
    user_type: str = "company"

class CompanySignupResponseDto(BaseModel):
    message: str
    company_id: int
    email: str
    user_type: str = "company"
