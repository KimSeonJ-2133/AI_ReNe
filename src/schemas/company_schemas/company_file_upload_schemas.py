"""
기업 채용 공고 파일 업로드 관련 Schema 정의
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class JDUploadResponse(BaseModel):
    """
    기업 채용 공고 파일 업로드 성공 시 응답 모델
    """
    file_id: str = Field(..., description = "생성된 파일 고유 ID")
    min_rcs_level: str = Field(..., description = "최소 요구 RCS 레벨 (예: Lv.3)")
    target_rcs_level: str = Field(..., description = "목표 RCS 레벨 (예: Lv.5)")
    jrs_markdown: str = Field(..., description = "JRS 포맷으로 변환된 마크다운 문자열")
    created_at: str = Field(..., description = "생성 시간 (ISO 8601 형식)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "comp_jd_20241126_143022",
                "min_rcs_level": "Lv.3",
                "target_rcs_level": "Lv.5",
                "jrs_markdown": "# [1. Basic Target Profile]\n- **Job Title:** Backend Developer...",
                "created_at": "2024-11-26T14:30:22.123456"
            }
        }
    )


class ParsedJRSData(BaseModel):
    """
    파싱된 JRS 데이터의 구조화된 형태
    """
    basic_profile: str = Field(..., description = "기본 타겟 프로필 섹션")
    hard_skills: str = Field(..., description = "Hard Skill Criteria 섹션")
    soft_skills: str = Field(..., description = "Soft Skill & Culture Criteria 섹션")
    domain: str = Field(..., description = "Domain & Constraints 섹션")
    additional_info: Optional[str] = Field(None, description = "추가 정보 섹션")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "basic_profile": "# [1. Basic Target Profile]\n- **Job Title:** Backend Developer...",
                "hard_skills": "# [2. Hard Skill Criteria]\n## [Critical Stack]...",
                "soft_skills": "# [3. Soft Skill & Culture Criteria]\n## [Collaboration Style]...",
                "domain": "# [4. Domain & Constraints]\n- **Industry:** E-Commerce...",
                "additional_info": "# [5. Additional Information]\n- **Work Location:** 서울..."
            }
        }
    )


class JRSErrorResponse(BaseModel):
    """
    JRS 파싱 실패 시 에러 응답 모델
    """
    error_code: str = Field(..., description = "에러 코드")
    error_message: str = Field(..., description = "에러 메시지")
    detail: Optional[str] = Field(None, description = "상세 에러 정보")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "JRS_PARSE_FAILED",
                "error_message": "채용 공고 파싱에 실패했습니다.",
                "detail": "LLM 응답 형식이 유효하지 않습니다."
            }
        }
    )


class CompanyIntroUploadResponse(BaseModel):
    """
    기업 소개서 파일 업로드 성공 시 응답 모델
    """
    file_id: str = Field(..., description = "생성된 파일 고유 ID")
    markdown_content: str = Field(..., description = "추출된 마크다운 내용")
    created_at: str = Field(..., description = "생성 시간 (ISO 8601 형식)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "comp_intro_20241126_143022",
                "markdown_content": "# Company Introduction\nWe are...",
                "created_at": "2024-11-26T14:30:22.123456"
            }
        }
    )
