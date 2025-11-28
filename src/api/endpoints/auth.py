from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.deps import get_db
from src.services.auth_service import AuthService
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.company_schemas.company_request_dto import CompanySignupRequestDto, CompanyLoginRequestDto

router = APIRouter(prefix="/auth", tags=["Auth"])

# ==========================================
# 1. 구직자 (Jobseeker) 인증
# ==========================================

@router.post("/signup/jobseeker", status_code=status.HTTP_201_CREATED)
def signup_jobseeker(
    request: JobseekerSignupRequestDto, 
    db: Session = Depends(get_db)
):
    """
    구직자 회원가입
    """
    auth_service = AuthService(db)
    new_jobseeker = auth_service.signup_jobseeker(request)
    
    return {
        "message": "회원가입이 완료되었습니다.",
        "user_id": new_jobseeker.id,
        "email": new_jobseeker.email,
        "user_type": "jobseeker"
    }

@router.post("/login/jobseeker")
def login_jobseeker(
    request: JobseekerLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    구직자 로그인
    """
    auth_service = AuthService(db)
    user = auth_service.login_jobseeker(request)
        
    return {
        "message": "로그인 성공",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "user_type": "jobseeker"
    }


# ==========================================
# 2. 기업 (Company) 인증
# ==========================================

@router.post("/signup/company", status_code=status.HTTP_201_CREATED)
def signup_company(
    request: CompanySignupRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 회원가입
    """
    auth_service = AuthService(db)
    new_company = auth_service.signup_company(request)
    
    return {
        "message": "기업 회원가입이 완료되었습니다.",
        "company_id": new_company.id,
        "email": new_company.email,
        "user_type": "company"
    }

@router.post("/login/company")
def login_company(
    request: CompanyLoginRequestDto,
    db: Session = Depends(get_db)
):
    """
    기업 로그인
    """
    auth_service = AuthService(db)
    company = auth_service.login_company(request)
        
    return {
        "message": "로그인 성공",
        "company_id": company.id,
        "name": company.name,
        "email": company.email,
        "user_type": "company"
    }
