from pydantic import BaseModel

class JobseekerLoginRequestDto(BaseModel):
    email: str
    password: str

class JobseekerSignupRequestDto(BaseModel):
    email: str
    password: str
    age: int
    