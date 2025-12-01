from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.deps import get_db
from src.services.auth_service.auth_service import AuthService
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.company_schemas.company_request_dto import CompanySignupRequestDto, CompanyLoginRequestDto
from src.schemas.jobseeker_schemas.jobseeker_response_dto import JobseekerSignupResponseDto, JobseekerLoginResponseDto
from src.schemas.company_schemas.company_response_dto import CompanySignupResponseDto, CompanyLoginResponseDto

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==========================================
# 1. 구직자 (Jobseeker) 인증
# ==========================================

@router.post("/signup/jobseeker", status_code=status.HTTP_201_CREATED, response_model=JobseekerSignupResponseDto)
def signup_jobseeker(
    request: JobseekerSignupRequestDto, 
    db: Session = Depends(get_db)
):
    """
    구직자 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_jobseeker(request)

@router.post("/login/jobseeker", response_model=JobseekerLoginResponseDto)
def login_jobseeker(
    request: JobseekerLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    구직자 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_jobseeker(request)


# ==========================================
# 2. 기업 (Company) 인증
# ==========================================

@router.post("/signup/company", status_code=status.HTTP_201_CREATED, response_model=CompanySignupResponseDto)
def signup_company(
    request: CompanySignupRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_company(request)

@router.post("/login/company", response_model=CompanyLoginResponseDto)
def login_company(
    request: CompanyLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_company(request)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
                          
from src.api.deps import get_db
from src.services.auth_service.auth_service import AuthService
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.company_schemas.company_request_dto import CompanySignupRequestDto, CompanyLoginRequestDto
from src.schemas.jobseeker_schemas.jobseeker_response_dto import JobseekerSignupResponseDto, JobseekerLoginResponseDto
from src.schemas.company_schemas.company_response_dto import CompanySignupResponseDto, CompanyLoginResponseDto

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==========================================
# 1. 구직자 (Jobseeker) 인증
# ==========================================

@router.post("/signup/jobseeker", status_code=status.HTTP_201_CREATED, response_model=JobseekerSignupResponseDto)
def signup_jobseeker(
    request: JobseekerSignupRequestDto, 
    db: Session = Depends(get_db)
):
    """
    구직자 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_jobseeker(request)

@router.post("/login/jobseeker", response_model=JobseekerLoginResponseDto)
def login_jobseeker(
    request: JobseekerLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    구직자 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_jobseeker(request)


# ==========================================
# 2. 기업 (Company) 인증
# ==========================================

@router.post("/signup/company", status_code=status.HTTP_201_CREATED, response_model=CompanySignupResponseDto)
def signup_company(
    request: CompanySignupRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_company(request)

@router.post("/login/company", response_model=CompanyLoginResponseDto)
def login_company(
    request: CompanyLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_company(request)