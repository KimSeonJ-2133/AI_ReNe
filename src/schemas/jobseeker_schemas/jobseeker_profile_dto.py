from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class EducationDto(BaseModel):
    school_name: str
    major: str
    period: str
    status: Optional[str] = None

class CareerDto(BaseModel):
    company_name: str
    role: str
    period: str
    description: Optional[str] = None

class ProjectDto(BaseModel):
    name: str
    role: str
    description: str
    tech_stack: List[str] = []

class JobseekerProfileResponseDto(BaseModel):
    # Basic Info
    user_id: int
    name: str
    email: str
    phone: str
    address: str
    birthdate: str
    gender: str
    profile_image_url: Optional[str] = None # 추후 구현
    brief_introduction: Optional[str] = None
    links: List[Dict[str, str]] = [] # [{"type": "github", "url": "..."}, ...]

    # Stats / Levels
    ncs_level: Optional[int] = None
    rcs_level: Optional[int] = None
    talent_type: Optional[str] = None
    mbti: Optional[str] = None
    verification_badge: Optional[str] = None

    # Skills
    main_skills: List[str] = []

    # Details
    education: List[str] = [] # 문자열 리스트로 단순화 (Resume 파싱 결과가 문자열 리스트일 수 있음)
    career: List[Dict[str, Any]] = [] # Resume의 work_experience 구조 따름
    certifications: List[str] = []
    
    # Portfolio
    projects: List[Dict[str, Any]] = [] # Portfolio의 project_details 구조 따름

    class Config:
        from_attributes = True
