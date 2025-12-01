import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import UploadFile
import sys
import os

# 환경 변수 설정 (임포트 전에 설정해야 Settings 검증 통과)
os.environ["ELEVENLABS_API_KEY"] = "test_api_key"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3306"

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.services.file_upload_service.seeker_file_upload_service import process_file_upload
from src.services.file_upload_service.company_file_upload_service import process_company_file_upload

# ==========================================
# Seeker File Upload Service Tests
# ==========================================

@patch("src.services.file_upload_service.seeker_file_upload_service.save_uploaded_file")
@patch("src.services.file_upload_service.seeker_file_upload_service.extract_text_from_file")
@patch("src.services.file_upload_service.seeker_file_upload_service.parse_resume_with_llm")
@patch("src.services.file_upload_service.seeker_file_upload_service.validate_parsing_result")
@pytest.mark.asyncio
async def test_process_seeker_file_upload(
    mock_validate, mock_parse_llm, mock_extract_text, mock_save_file
):
    """
    SeekerFileUploadService 단위 테스트
    - 파일 저장 -> 텍스트 추출 -> LLM 파싱 -> 검증 흐름 확인
    """
    # Mock 설정
    mock_save_file.return_value = "/tmp/fake_path.pdf"
    mock_extract_text.return_value = "이력서 내용입니다."
    
    mock_parsing_result = {
        "ncs_level": "Lv.3",
        "rcs_level": "Lv.4",
        "markdown_content": "# Resume",
        "parsed_data": {"name": "Test User"}
    }
    mock_parse_llm.return_value = mock_parsing_result
    mock_validate.return_value = True
    
    # Mock Input
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "resume.pdf"
    mock_db = MagicMock()
    
    # Service 호출
    result = await process_file_upload(
        session_id="test_session",
        file_type="resume",
        file=mock_file,
        user_id="1",
        db=mock_db
    )
    
    # 검증
    assert result.file_id.startswith("file_")
    # assert result.status == "success" # status 필드 없음
    assert result.ncs_level == "Lv.3"
    assert result.rcs_level == "Lv.4"
    
    # 호출 순서 및 인자 확인
    mock_save_file.assert_called_once()
    mock_extract_text.assert_called_once_with("/tmp/fake_path.pdf")
    mock_parse_llm.assert_called_once()
    mock_validate.assert_called_once()

# ==========================================
# Company File Upload Service Tests
# ==========================================

@patch("src.services.file_upload_service.company_file_upload_service.save_uploaded_file")
@patch("src.services.file_upload_service.company_file_upload_service.extract_text_from_file")
@patch("src.services.file_upload_service.company_file_upload_service.parse_jd_with_llm")
@pytest.mark.asyncio
async def test_process_company_file_upload(
    mock_parse_jd, mock_extract_text, mock_save_file
):
    """
    CompanyFileUploadService 단위 테스트
    - 파일 저장 -> 텍스트 추출 -> LLM 파싱 흐름 확인
    """
    # Mock 설정
    mock_save_file.return_value = "/tmp/fake_jd.pdf"
    mock_extract_text.return_value = "채용 공고 내용입니다."
    
    mock_jd_result = {
        "min_rcs_level": "Lv.3",
        "target_rcs_level": "Lv.5",
        "jrs_markdown": "# Job Description",
        "parsed_data": {"title": "Backend Dev"}
    }
    mock_parse_jd.return_value = mock_jd_result
    
    # Mock Input
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "jd.pdf"
    mock_db = MagicMock()
    
    # Service 호출
    result = await process_company_file_upload(
        session_id="test_session",
        file_type="jd",
        file=mock_file,
        user_id="1",
        db=mock_db
    )
    
    # 검증
    assert result.file_id.startswith("comp_jd_")
    # assert result.status == "success" # status 필드 없음
    assert result.min_rcs_level == "Lv.3"
    assert result.target_rcs_level == "Lv.5"
    
    # 호출 확인
    mock_save_file.assert_called_once()
    mock_extract_text.assert_called_once_with("/tmp/fake_jd.pdf")
    mock_parse_jd.assert_called_once()
