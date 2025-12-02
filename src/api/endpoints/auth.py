from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.deps import get_db
from src.services.auth_service.auth_service import AuthService
from src.schemas.jobseeker_schemas import jobseeker_request_dto
from src.schemas.company_schemas import company_request_dto
from src.schemas.jobseeker_schemas import jobseeker_response_dto
from src.schemas.company_schemas import company_response_dto

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# ==========================================
# 1. 구직자 (Jobseeker) 
# ==========================================

@auth_router.post("/signup/jobseeker", status_code=status.HTTP_201_CREATED, response_model=jobseeker_response_dto.JobseekerSignupResponseDto)
def signup_jobseeker(
    request: jobseeker_request_dto.JobseekerSignupRequestDto, 
    db: Session = Depends(get_db)
):
    """
    구직자 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_jobseeker(request)

@auth_router.post("/login/jobseeker", response_model=jobseeker_response_dto.JobseekerLoginResponseDto)
def login_jobseeker(
    request: jobseeker_request_dto.JobseekerLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    구직자 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_jobseeker(request)


# ==========================================
# 2. 기업 (Company)
# ==========================================

@auth_router.post("/signup/company", status_code=status.HTTP_201_CREATED, response_model=company_response_dto.CompanySignupResponseDto)
def signup_company(
    request: company_request_dto.CompanySignupRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 회원가입
    """
    auth_service = AuthService(db)
    return auth_service.signup_company(request)

@auth_router.post("/login/company", response_model=company_response_dto.CompanyLoginResponseDto)
def login_company(
    request: company_request_dto.CompanyLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 로그인
    """
    auth_service = AuthService(db)
    return auth_service.login_company(request)
