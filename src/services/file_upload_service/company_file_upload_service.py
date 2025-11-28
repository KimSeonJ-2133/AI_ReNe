"""
기업 채용 공고 파일 업로드를 처리하는 Service Layer
"""

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
    if not validate_file_extension(file.filename):
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
    
    # 6. DB 저장 (현재 DB 스키마와 불일치하여 주석 처리)
    """
    if db and user_id:
        # RecruitmentNotice 테이블이 있다고 가정
        new_notice = RecruitmentNotice(
            company_id=int(user_id),
            title=file.filename,
            content=text_content,
            responsibilities=parsing_result["parsed_data"].get("responsibilities", {}),
            requirements=parsing_result["parsed_data"].get("requirements", {}),
            ncs_level=parsing_result["min_rcs_level"], # 매핑 필요
            rcs_level=parsing_result["target_rcs_level"], # 매핑 필요
            jrs_markdown=parsing_result["jrs_markdown"]
        )
        db.add(new_notice)
        db.commit()
        db.refresh(new_notice)
        print(f"[Service] DB 저장 완료 - ID: {new_notice.id}")
    """
    
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
