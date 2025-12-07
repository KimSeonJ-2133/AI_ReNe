from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.orm import Session
import os
from uuid import uuid4

from api.deps import get_db
from services.file_upload_service.seeker_file_upload_service import process_file_upload
from services.file_upload_service.company_file_upload_service import process_company_file_upload
from schemas.jobseeker_schemas.seeker_file_upload_schemas import FileUploadResponse
from schemas.company_schemas.company_file_upload_schemas import JDUploadResponse

upload_router = APIRouter(prefix="/upload", tags=["File Upload"])


@upload_router.post("/jobseeker-docs", response_model=FileUploadResponse)
async def upload_jobseeker_docs(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    구직자 문서 업로드 (이력서 또는 포트폴리오)
    
    Parameters:
    - **file**: 업로드 파일 (파일명 형식: {ID}_{Timestamp}.pdf)
      - 예: jobplz_2512072109.pdf
    - **file_type**: "resume" 또는 "portfolio"
    
    Returns:
    - file_id: 파일 고유 ID
    - ncs_level: 파싱된 NCS 레벨
    - rcs_level: 파싱된 RCS 레벨
    - parsed_markdown: 전체 마크다운 내용
    - created_at: 생성 시간
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/upload/jobseeker-docs" \\
      -F "file=@jobplz_2512072109.pdf" \\
      -F "file_type=resume"
    ```
    """
    if file_type not in ["resume", "portfolio"]:
        raise HTTPException(
            status_code=400,
            detail="file_type은 'resume' 또는 'portfolio' 중 하나여야 합니다."
        )
    
    # 파일명에서 user_id 추출 (예: jobplz_2512072109.pdf -> jobplz)
    filename_without_ext = os.path.splitext(file.filename)[0]
    user_id = filename_without_ext.split('_')[0]
    
    # 세션 ID 생성 (기존 서비스가 요구)
    session_id = str(uuid4())
    
    return process_file_upload(
        session_id=session_id,
        file_type=file_type,
        file=file,
        user_id=user_id,
        db=db
    )


@upload_router.post("/company-docs", response_model=JDUploadResponse)
async def upload_company_docs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    기업 채용 공고 업로드
    
    Parameters:
    - **file**: 업로드 파일 (파일명 형식: {ID}_{Timestamp}.pdf)
      - 예: companyabc_2512072109.pdf
    
    Returns:
    - file_id: 파일 고유 ID
    - min_rcs_level: 최소 요구 RCS 레벨
    - target_rcs_level: 목표 RCS 레벨
    - jrs_markdown: JRS 포맷 마크다운 (전체 내용)
    - created_at: 생성 시간
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/upload/company-docs" \\
      -F "file=@companyabc_2512072109.pdf"
    ```
    """
    # 파일명에서 company_id 추출 (예: companyabc_2512072109.pdf -> companyabc)
    filename_without_ext = os.path.splitext(file.filename)[0]
    company_id = filename_without_ext.split('_')[0]
    
    # 세션 ID 생성 (기존 서비스가 요구)
    session_id = str(uuid4())
    
    return process_company_file_upload(
        session_id=session_id,
        file_type="jd",
        file=file,
        user_id=company_id,
        db=db
    )
