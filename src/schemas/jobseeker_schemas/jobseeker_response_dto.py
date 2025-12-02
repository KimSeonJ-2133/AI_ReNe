from pydantic import BaseModel
from typing import Optional

class JobseekerResponseDto(BaseModel):
    user_id: int
    email: str
    name: str
    user_type: str = "jobseeker"

class JobseekerLoginResponseDto(BaseModel):
    message: str
    user_id: int
    name: str
    email: str
    user_type: str = "jobseeker"

class JobseekerSignupResponseDto(BaseModel):
    message: str
    user_id: int
    email: str
    user_type: str = "jobseeker"


