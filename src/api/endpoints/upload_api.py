from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from typing import Optional

from api.deps import get_db
from src.models.user import Jobseeker
from services.file_upload_service.seeker_file_upload_service import process_file_upload
from services.file_upload_service.company_file_upload_service import process_company_file_upload
from schemas.jobseeker_schemas.seeker_file_upload_schemas import FileUploadResponse
from schemas.company_schemas.company_file_upload_schemas import JDUploadResponse

upload_router = APIRouter(prefix="/upload", tags=["File Upload"])

@upload_router.post("/jobseeker-docs", response_model=FileUploadResponse)
async def upload_jobseeker_docs(
    file: UploadFile = File(...),
    file_type: str = Form("portfolio"),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    구직자 문서 업로드 (이력서 또는 포트폴리오)
    
    Parameters:
    - **file**: 업로드 파일 (파일명에서 사용자 이메일 추출. 예: 01_jobplz.pdf -> jobplz)
    - **file_type**: "resume" 또는 "portfolio"
    - **email**: 사용자 이메일 (선택 사항. 제공 시 파일명 파싱보다 우선함)
    
    Returns:
    - file_id: 파일 고유 ID
    - ncs_level: 파싱된 NCS 레벨
    - rcs_level: 파싱된 RCS 레벨
    - parsed_markdown: 전체 마크다운 내용
    - created_at: 생성 시간
    """
    if file_type not in ["resume", "portfolio"]:
        raise HTTPException(
            status_code=400,
            detail="file_type은 'resume' 또는 'portfolio' 중 하나여야 합니다."
        )
    
    # 이메일이 제공된 경우 우선 사용
    if email:
        username = email
    else:
        # 파일명에서 username(email) 추출
        # 로직: {순서}_{username}.{확장자} 또는 {username}.{확장자}
        # 예: "01_jobplz.pdf" -> "jobplz"
        filename = file.filename
        name_without_ext = os.path.splitext(filename)[0]
        parts = name_without_ext.split('_')
        
        if len(parts) >= 2:
            username = parts[-1]
        else:
            username = name_without_ext
        
    # DB에서 사용자 조회 (email 기준)
    # DB에서 사용자 조회 (email 기준)
    jobseeker = db.query(Jobseeker).filter(Jobseeker.email == username).first()
    
    if not jobseeker:
        raise HTTPException(
            status_code=404,
            detail=f"해당 이메일({username})을 가진 구직자를 찾을 수 없습니다."
        )
    
    user_id = jobseeker.id
    
    # 세션 ID 생성 (기존 서비스가 요구)
    session_id = str(uuid4())
    
    return await process_file_upload(
        session_id=session_id,
        file_type=file_type,
        file=file,
        user_id=user_id,
        db=db
    )


@upload_router.post("/company-docs", response_model=JDUploadResponse)
async def upload_company_docs(
    file: UploadFile = File(...),
    company_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    기업 채용 공고 업로드
    
    Parameters:
    - **file**: 업로드 파일 (PDF, DOCX 등)
    - **company_id**: 기업 ID (DB PK)
    
    Returns:
    - file_id: 파일 고유 ID
    - min_rcs_level: 최소 요구 RCS 레벨
    - target_rcs_level: 목표 RCS 레벨
    - jrs_markdown: JRS 포맷 마크다운 (전체 내용)
    - created_at: 생성 시간
    """
    
    # 세션 ID 생성 (기존 서비스가 요구)
    session_id = str(uuid4())
    
    return await process_company_file_upload(
        session_id=session_id,
        file_type="jd",
        file=file,
        user_id=company_id,
        db=db
    )
