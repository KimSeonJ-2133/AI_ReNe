"""파일 업로드 및 파싱 비즈니스 로직"""
import os
import sys
import uuid
from typing import Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.file_storage_utils import save_uploaded_file
from agents.tools.file_text_extractor import extract_text_from_file, get_text_preview
from agents.seeker_file_upload_agent import parse_resume_with_llm, validate_parsing_result
from schemas.seeker_file_upload_schemas import FileUploadResponse


async def process_file_upload(
    session_id: str,
    file_type: str,
    file: UploadFile,
    user_id: str
) -> Dict[str, Any]:
    """
    파일 업로드부터 LLM 파싱까지 전체 프로세스 처리
    
    Args:
        session_id: 세션 ID
        file_type: 파일 타입 ("resume" 또는 "portfolio")
        file: FastAPI UploadFile 객체
        user_id: 사용자 ID
    
    Returns:
        Dict[str, Any]: 처리 결과
            - file_id: 생성된 파일 ID
            - ncs_level: NCS 레벨
            - rcs_level: RCS 레벨
            - parsed_markdown: 파싱된 마크다운
            - created_at: 생성 시간
    
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
        
        # 6. DB 저장 (현재는 주석 처리)
        """
        # TODO: DB 연동 시 활성화
        from repositories.seeker_file_upload_repository import create_resume_record
        
        db_data = {
            "jobseeker_id": int(user_id),
            "file_id": file_id,
            "file_path": file_path,
            "original_filename": file.filename,
            "file_type": file_type,
            "parsed_markdown": parsing_result["markdown_content"],
            "parsed_json": parsing_result["parsed_data"],
            "ncs_level": parsing_result["ncs_level"],
            "rcs_level": parsing_result["rcs_level"]
        }
        
        resume_record = create_resume_record(db_session, db_data)
        print(f"[Service] DB 저장 완료 - Record ID: {resume_record.id}")
        """
        
        # 7. 응답 데이터 구성
        response = {
            "file_id": file_id,
            "ncs_level": parsing_result["ncs_level"],
            "rcs_level": parsing_result["rcs_level"],
            "parsed_markdown": parsing_result["markdown_content"],
            "created_at": datetime.now().isoformat()
        }
        
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
