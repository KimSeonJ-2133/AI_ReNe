#모듈 정의 : 기업 채용 공고(JD) 파일 업로드 및 파싱 처리 - Service Module
#연결 모듈 : src/api/endpoints/main.py (API),
#  src/agents/company_jd_parser_agent.py (Agent)

import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.utils.file_storage_utils import save_uploaded_file, validate_file_extension
from src.agents.tools.file_text_extractor import extract_text_from_file
from src.agents.company_jd_parser_agent import parse_jd_with_llm
from src.schemas.company_schemas.company_file_upload_schemas import JDUploadResponse
# from src.models.recruitment import RecruitmentNotice  # [가상 모델] 추후 구현 필요


async def process_company_file_upload(
    session_id: str,
    file_type: str,
    file: UploadFile,
    user_id: Optional[str] = None,
    db: Session = None  # DB 세션 추가
) -> JDUploadResponse:
    """
    기업 채용 공고 파일 업로드 전체 프로세스 처리
    
    Flow:
    1. 파일 확장자 검증
    2. 파일 저장 (data/uploads/{user_id}/company_jd/)
    3. 텍스트 추출
    4. LLM으로 JRS 포맷 파싱
    5. (DB 저장 - 추후 활성화)
    6. 결과 반환
    
    Args:
        session_id: 세션 ID
        file_type: 파일 유형 (jd, job_description 등)
        file: 업로드된 파일 객체
        user_id: 사용자 ID (기업 ID)
        
    Returns:
        {
            "file_id": str,
            "min_rcs_level": str,
            "target_rcs_level": str,
            "jrs_markdown": str,
            "parsed_data": dict,
            "created_at": str
        }
    """
    # 1. 파일 검증
    allowed_extensions = [".pdf", ".docx", ".txt"]
    if not validate_file_extension(file.filename, allowed_extensions):
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file.filename}")
    
    # 2. 파일 저장
    user_folder = user_id if user_id else "anonymous"
    file_path = await save_uploaded_file(
        file = file,
        user_id = user_folder,
        file_type = "company_jd"  # company_jd 디렉토리에 저장
    )
    
    # 3. 텍스트 추출
    try:
        text_content = extract_text_from_file(file_path)
        print(f"[INFO] 채용 공고 텍스트 추출 완료: {len(text_content)} 글자")
    except Exception as e:
        raise RuntimeError(f"채용 공고 텍스트 추출 실패: {str(e)}")
    
    # 4. LLM 파싱
    try:
        parsing_result = parse_jd_with_llm(
            text_content = text_content,
            file_type = os.path.splitext(file.filename)[1][1:]  # 확장자 (pdf, docx 등)
        )
        print(f"[INFO] JRS 파싱 완료 - Min: {parsing_result['min_rcs_level']}, Target: {parsing_result['target_rcs_level']}")
    except Exception as e:
        raise RuntimeError(f"JRS 파싱 실패: {str(e)}")
    
    # 5. 파일 ID 생성
    file_id = f"comp_jd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 6. DB 저장 (활성화)
    if db and user_id:
        from src.models.user import Company, JobGroup
        from src.models.document import RecruitmentNotice
        
        # Company 확인 및 자동 생성
        company = db.query(Company).filter(Company.email == f"{user_id}@temp.com").first()
        
        if not company:
            print(f"[Service] Company 자동 생성 중... (company_id: {user_id})")
            company = Company(
                name=user_id,
                email=f"{user_id}@temp.com",
                password="temp_password",
                address="Unknown",
                business_number="000-00-00000",
                policy_agree_bool=True
            )
            db.add(company)
            db.flush()
            print(f"[Service] Company 생성 완료 - ID: {company.id}")
        
        # JobGroup 확인 및 자동 생성
        job_group = db.query(JobGroup).filter(JobGroup.company_id == company.id).first()
        
        if not job_group:
            print(f"[Service] JobGroup 자동 생성 중...")
            job_group = JobGroup(
                company_id=company.id,
                name="기본 직군"
            )
            db.add(job_group)
            db.flush()
            print(f"[Service] JobGroup 생성 완료 - ID: {job_group.id}")
        
        # RecruitmentNotice 저장 (markdown_content에 모든 정보 포함)
        new_notice = RecruitmentNotice(
            job_group_id=job_group.id,
            markdown_content=parsing_result["jrs_markdown"]
        )
        db.add(new_notice)
        db.commit()
        db.refresh(new_notice)
        print(f"[Service] RecruitmentNotice 저장 완료 - ID: {new_notice.id}")
    
    # 7. 결과 반환
    return JDUploadResponse(
        file_id=file_id,
        min_rcs_level=parsing_result["min_rcs_level"],
        target_rcs_level=parsing_result["target_rcs_level"],
        jrs_markdown=parsing_result["jrs_markdown"],
        created_at=datetime.now().isoformat()
    )


def get_parsed_jd(file_id: str) -> Optional[Dict[str, Any]]:
    """
    저장된 JRS 데이터 조회 (DB 연동 후 구현)
    
    Args:
        file_id: 파일 ID
        
    Returns:
        파싱된 JRS 데이터 또는 None
    """
    # TODO: DB에서 조회
    # from src.repositories.company_jd_repository import get_jd_by_file_id
    # return get_jd_by_file_id(file_id)
    
    return None
