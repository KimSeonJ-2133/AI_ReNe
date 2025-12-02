from pydantic import BaseModel
from typing import Optional

class CompanyLoginRequestDto(BaseModel):
    email: str
    password: str

class CompanySignupRequestDto(BaseModel):
    email: str
    password: str
    name: str
    company_scale: Optional[str] = None
    address: str
    business_number: str
    policy_agree_bool: bool = False