"""파일 업로드 관련 Request/Response 샘플 스키마"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class FileUploadResponse(BaseModel):
    """파일 업로드 후 반환되는 응답"""
    file_id: str = Field(..., description = "생성된 파일 ID")
    ncs_level: Optional[str] = Field(None, description = "NCS 레벨 (예: 'Lv. 4 (Analysis)')")
    rcs_level: Optional[str] = Field(None, description = "RCS 레벨 (예: 'Lv. 4 Solver')")
    parsed_markdown: Optional[str] = Field(None, description = "파싱된 마크다운 전체 내용")
    created_at: str = Field(..., description = "생성 시간")


class ParsedResumeData(BaseModel):
    """LLM이 파싱한 이력서 데이터 구조"""
    ncs_level: str = Field(..., description = "NCS 레벨")
    rcs_level: str = Field(..., description = "RCS 레벨")
    basic_info: Dict[str, Any] = Field(..., description = "기본 정보 (이름, 연락처 등)")
    summary: Dict[str, Any] = Field(..., description = "레벨 추론 근거")
    hard_facts: Dict[str, Any] = Field(..., description = "학력, 자격증, 스킬셋")
    history: List[Dict[str, Any]] = Field(..., description = "경력 사항")
    portfolio: List[Dict[str, Any]] = Field(..., description = "포트폴리오 및 프로젝트")
    markdown_content: str = Field(..., description = "전체 마크다운 텍스트")


class ParsingErrorResponse(BaseModel):
    """파싱 실패 시 에러 응답"""
    error: str = Field(..., description = "에러 메시지")
    detail: Optional[str] = Field(None, description = "상세 에러 정보")
