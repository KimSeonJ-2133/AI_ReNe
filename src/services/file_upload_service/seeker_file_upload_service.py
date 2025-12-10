#모듈 정의 : 구직자 이력서 및 포트폴리오 파일 업로드 및 파싱 처리 - Service Module
#연결 모듈 : src/api/endpoints/main.py (API),
#  src/agents/seeker_file_upload_agent.py (Agent)
import os
import sys
import uuid
from typing import Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.models.document import Resume, Portfolio  # 오타 주의: documnet

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.file_storage_utils import save_uploaded_file
from agents.tools.file_text_extractor import extract_text_from_file, get_text_preview
from agents.seeker_file_upload_agent import parse_resume_with_llm, validate_parsing_result
from schemas.jobseeker_schemas.seeker_file_upload_schemas import FileUploadResponse


async def process_file_upload(
    session_id: str,
    file_type: str,
    file: UploadFile,
    user_id: str,
    db: Session = None  # DB 세션 추가
) -> FileUploadResponse:
    """
    파일 업로드부터 LLM 파싱까지 전체 프로세스 처리
    
    Args:
        session_id: 세션 ID
        file_type: 파일 타입 ("resume" 또는 "portfolio")
        file: FastAPI UploadFile 객체
        user_id: 사용자 ID
    
    Returns:
        FileUploadResponse: 처리 결과 DTO
    
    Raises:
        HTTPException: 처리 중 오류 발생 시
    """
    file_id = None
    file_path = None
    
    try:
        # 1. 파일 ID 생성
        file_id = f"file_{uuid.uuid4().hex[:12]}"
        print(f"[Service] 파일 처리 시작 - File ID: {file_id}")
        
        # 2. 파일 저장
        print(f"[Service] 파일 저장 중... (user_id: {user_id}, file_type: {file_type})")
        file_path = await save_uploaded_file(file, user_id, file_type)
        print(f"[Service] 파일 저장 완료: {file_path}")
        
        # 3. 텍스트 추출
        print(f"[Service] 텍스트 추출 중...")
        text_content = extract_text_from_file(file_path)
        print(f"[Service] 텍스트 추출 완료 (길이: {len(text_content)} 자)")
        print(f"[Service] 미리보기:\n{get_text_preview(text_content, 300)}\n")
        
        # 4. LLM 파싱
        print(f"[Service] LLM 파싱 시작...")
        parsing_result = parse_resume_with_llm(text_content, file_type)
        
        # 5. 결과 검증
        if not validate_parsing_result(parsing_result):
            raise Exception("LLM 파싱 결과가 유효하지 않습니다.")
        
        print(f"[Service] LLM 파싱 완료!")
        print(f"  - NCS Level: {parsing_result['ncs_level']}")
        print(f"  - RCS Level: {parsing_result['rcs_level']}")
        
        # 6. RCS/NCS 레벨 변환 (문자열 -> 정수)
        def extract_level_number(level_str: str) -> int:
            """'Lv. 4 (Analysis)' -> 4"""
            try:
                if "Lv." in level_str or "Lv" in level_str:
                    import re
                    match = re.search(r'Lv\.?\s*(\d+)', level_str)
                    if match:
                        return int(match.group(1))
                return 1  # 기본값
            except Exception:
                return 1
        
        ncs_level_int = extract_level_number(parsing_result['ncs_level'])
        rcs_level_int = extract_level_number(parsing_result['rcs_level'])
        
        # 7. DB 저장 (활성화)
        if db:
            # Jobseeker 확인 및 자동 생성
            from src.models.user import Jobseeker
            from datetime import date
            
            jobseeker = db.query(Jobseeker).filter(Jobseeker.email == f"{user_id}@temp.com").first()
            
            if not jobseeker:
                print(f"[Service] Jobseeker 자동 생성 중... (user_id: {user_id})")
                jobseeker = Jobseeker(
                    name=user_id,
                    email=f"{user_id}@temp.com",
                    password="temp_password",
                    phone="010-0000-0000",
                    birthdate=date(2000, 1, 1),
                    gender="Unknown",
                    address="Unknown",
                    verified_grade="NOT_VERIFIED",
                    is_docs_submit="NONE"
                )
                db.add(jobseeker)
                db.flush()
                print(f"[Service] Jobseeker 생성 완료 - ID: {jobseeker.id}")
            
            if file_type == "resume":
                new_record = Resume(
                    jobseeker_id=jobseeker.id,
                    brief_self_introduction=parsing_result["parsed_data"].get("brief_self_introduction", "N/A"),
                    work_experience=parsing_result["parsed_data"].get("work_experience", []),
                    brief_project_introduction=parsing_result["parsed_data"].get("brief_project_introduction", []),
                    education=parsing_result["parsed_data"].get("education", []),
                    skills=parsing_result["parsed_data"].get("skills", []),
                    certifications=parsing_result["parsed_data"].get("certifications", []),
                    other_experience=parsing_result["parsed_data"].get("other_experience", []),
                    languages=parsing_result["parsed_data"].get("languages", []),
                    ncs_level=ncs_level_int,
                    rcs_level=rcs_level_int,
                    markdown_content=parsing_result["markdown_content"]
                )
                db.add(new_record)
            
            elif file_type == "portfolio":
                new_record = Portfolio(
                    jobseeker_id=jobseeker.id,
                    main_skills=parsing_result["parsed_data"].get("main_skills", []),
                    project_details=parsing_result["parsed_data"].get("project_details", []),
                    ncs_level=ncs_level_int,
                    rcs_level=rcs_level_int,
                    markdown_content=parsing_result["markdown_content"]
                )
                db.add(new_record)
            
            db.commit()
            db.refresh(new_record)
            print(f"[Service] DB 저장 완료 - Record ID: {new_record.id}")
        
        # 8. 응답 데이터 구성
        response = FileUploadResponse(
            file_id=file_id,
            ncs_level=parsing_result["ncs_level"],
            rcs_level=parsing_result["rcs_level"],
            parsed_markdown=parsing_result["markdown_content"],
            created_at=datetime.now().isoformat()
        )
        
        print(f"[Service] 처리 완료! File ID: {file_id}")
        return response
    
    except HTTPException as he:
        # FastAPI HTTPException은 그대로 전달
        raise he
    
    except Exception as e:
        print(f"[Service Error] 파일 처리 실패: {e}")
        
        # 오류 발생 시 저장된 파일 삭제
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[Service] 실패한 파일 삭제: {file_path}")
            except Exception as cleanup_error:
                print(f"[Service] 파일 정리 실패: {cleanup_error}")
        
        raise HTTPException(
            status_code = 500,
            detail = f"파일 처리 중 오류가 발생했습니다: {str(e)}"
        )


def get_parsed_profile(user_id: str, file_id: str) -> Dict[str, Any]:
    """
    파싱된 프로필 조회 (DB 연동 시 사용)
    
    Args:
        user_id: 사용자 ID
        file_id: 파일 ID
    
    Returns:
        Dict[str, Any]: 파싱된 프로필 데이터
    """
    # TODO: DB 연동 시 구현
    """
    from repositories.seeker_file_upload_repository import get_resume_by_file_id
    
    resume = get_resume_by_file_id(db_session, file_id)
    if not resume or resume.jobseeker_id != int(user_id):
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    
    return {
        "file_id": resume.file_id,
        "ncs_level": resume.ncs_level,
        "rcs_level": resume.rcs_level,
        "parsed_markdown": resume.parsed_markdown,
        "parsed_json": resume.parsed_json,
        "created_at": resume.created_at.isoformat()
    }
    """
    raise HTTPException(
        status_code = 501,
        detail = "DB 연동이 아직 구현되지 않았습니다."
    )
