from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.repositories.jobseeker_repository import JobseekerRepository
from src.repositories.company_repository import CompanyRepository
from src.models.user import Jobseeker, Company
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.company_schemas.company_request_dto import CompanySignupRequestDto, CompanyLoginRequestDto

class AuthService:
    def __init__(self, db: Session):
        self.jobseeker_repo = JobseekerRepository(db)
        self.company_repo = CompanyRepository(db)

    def signup_jobseeker(self, request: JobseekerSignupRequestDto) -> Jobseeker:
        # 이메일 중복 확인
        if self.jobseeker_repo.get_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 이메일입니다."
            )
        
        # 구직자 생성
        new_jobseeker = Jobseeker(
            email=request.email,
            password=request.password, # 보안: 프로토타입이므로 평문 저장
            name=request.name,
            phone=request.phone,
            birthdate=request.birthdate,
            gender=request.gender,
            address=request.address,
            policy_agree_bool=request.policy_agree_bool,
            verified_grade="NOT_VERIFIED", # 기본값 설정
            is_docs_submit="NONE"          # 기본값 설정
        )
        
        return self.jobseeker_repo.create(new_jobseeker)

    def login_jobseeker(self, request: JobseekerLoginRequestDto) -> Jobseeker:
        user = self.jobseeker_repo.get_by_email(request.email)
        
        # 인증 (프로토타입: 평문 비교)
        if not user or user.password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        return user

    def signup_company(self, request: CompanySignupRequestDto) -> Company:
        # 이메일 중복 확인
        if self.company_repo.get_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 등록된 이메일입니다."
            )
            
        # 기업 생성
        new_company = Company(
            email=request.email,
            password=request.password, # 보안: 프로토타입이므로 평문 저장
            name=request.name,
            company_scale=request.company_scale,
            address=request.address,
            business_number=request.business_number,
            policy_agree_bool=request.policy_agree_bool
        )
        
        return self.company_repo.create(new_company)

    def login_company(self, request: CompanyLoginRequestDto) -> Company:
        company = self.company_repo.get_by_email(request.email)
        
        # 인증 (프로토타입: 평문 비교)
        if not company or company.password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        return company
