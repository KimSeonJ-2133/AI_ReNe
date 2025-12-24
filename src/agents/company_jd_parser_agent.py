"""
기업 채용 공고(JD)를 분석하여 JRS(Job Requirement Specification) 포맷으로 변환하는 Agent
"""

import re
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.prompts.company_jd_parser_prompts import COMPANY_JD_PARSER_SYSTEM_PROMPT, COMPANY_DOC_CLASSIFIER_PROMPT


def classify_company_doc(text_content: str) -> Dict[str, Any]:
    """
    문서 내용을 분석하여 기업 소개서인지 채용 공고인지 분류
    
    Returns:
        {
            "doc_type": "COMPANY_INTRO" | "RECRUITMENT_NOTICE",
            "job_group": str | None
        }
    """
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0.0,
        api_key=settings.OPENAI_API_KEY,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    messages = [
        {"role": "system", "content": COMPANY_DOC_CLASSIFIER_PROMPT},
        {"role": "user", "content": f"Document Content:\n{text_content[:3000]}"} # 앞부분 3000자만 분석
    ]
    
    try:
        response = llm.invoke(messages)
        result = json.loads(response.content)
        return result
    except Exception as e:
        print(f"[Agent Error] 문서 분류 실패: {e}")
        # 기본값: 채용 공고로 가정하고 직군 없음
        return {"doc_type": "RECRUITMENT_NOTICE", "job_group": "Unknown"}


def parse_jd_with_llm(text_content: str, file_type: str = "text") -> Dict[str, Any]:
    """
    LLM을 사용하여 채용 공고 텍스트를 JRS 포맷으로 파싱
    
    Args:
        text_content: 채용 공고 텍스트 내용
        file_type: 파일 유형 (pdf, docx, text 등)
        
    Returns:
        Dict containing:
            - min_rcs_level: 최소 RCS 레벨 (str)
            - target_rcs_level: 목표 RCS 레벨 (str)
            - jrs_markdown: JRS 포맷으로 변환된 마크다운 문자열
            - parsed_data: 파싱된 구조화 데이터
    """
    # LLM 초기화
    llm = ChatOpenAI(
        model = "gpt-4.1-mini",
        temperature = 0.1,
        api_key = settings.OPENAI_API_KEY
    )
    
    # 사용자 프롬프트 생성
    user_prompt = f"""다음은 채용 공고 텍스트입니다 (파일 형식: {file_type}).
        이 텍스트를 분석하여 JRS(Job Requirement Specification) 포맷으로 변환해주세요.

        ===== 채용 공고 원문 =====
        {text_content}
        ========================

        위 원문을 기반으로 JRS 포맷의 마크다운을 생성해주세요.
    """
    
    # LLM 호출
    messages = [
        {"role": "system", "content": COMPANY_JD_PARSER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm.invoke(messages)
    jrs_markdown = response.content.strip()
    
    # RCS 레벨 추출
    min_rcs_level = extract_min_rcs_level(jrs_markdown)
    target_rcs_level = extract_target_rcs_level(jrs_markdown)
    
    # 섹션별 파싱
    parsed_sections = parse_jrs_sections(jrs_markdown)
    
    result = {
        "min_rcs_level": min_rcs_level,
        "target_rcs_level": target_rcs_level,
        "jrs_markdown": jrs_markdown,
        "parsed_data": parsed_sections
    }
    
    # 결과 검증
    if not validate_jrs_result(result):
        raise ValueError("JRS 파싱 결과가 유효하지 않습니다.")
    
    return result


def extract_min_rcs_level(markdown_text: str) -> str:
    """
    JRS 마크다운에서 Min RCS Level 추출
    예: "Min Lv.3 (Player)" → "Lv.3"
    """
    pattern = r"Min\s+Lv\.(\d+)\s*\(([^)]+)\)"
    match = re.search(pattern, markdown_text)
    
    if match:
        level_num = match.group(1)
        return f"Lv.{level_num}"
    
    return "Unknown"


def extract_target_rcs_level(markdown_text: str) -> str:
    """
    JRS 마크다운에서 Target RCS Level 추출
    예: "Target Lv.5 (Architect)" → "Lv.5"
    """
    pattern = r"Target\s+Lv\.(\d+)\s*\(([^)]+)\)"
    match = re.search(pattern, markdown_text)
    
    if match:
        level_num = match.group(1)
        return f"Lv.{level_num}"
    
    return "Unknown"


def parse_jrs_sections(markdown_text: str) -> Dict[str, Any]:
    """
    JRS 마크다운을 섹션별로 파싱하여 구조화된 데이터로 변환
    
    Returns:
        {
            "basic_profile": str,  # [1. Basic Target Profile] 섹션
            "hard_skills": str,    # [2. Hard Skill Criteria] 섹션
            "soft_skills": str,    # [3. Soft Skill & Culture Criteria] 섹션
            "domain": str,         # [4. Domain & Constraints] 섹션
            "additional_info": str # [5. Additional Information] 섹션
        }
    """
    sections = {
        "basic_profile": "",
        "hard_skills": "",
        "soft_skills": "",
        "domain": "",
        "additional_info": ""
    }
    
    # 섹션 경계 패턴 정의
    section_patterns = [
        (r"#\s*\[1\.\s*Basic Target Profile\]", "basic_profile"),
        (r"#\s*\[2\.\s*Hard Skill Criteria\]", "hard_skills"),
        (r"#\s*\[3\.\s*Soft Skill & Culture Criteria", "soft_skills"),
        (r"#\s*\[4\.\s*Domain & Constraints\]", "domain"),
        (r"#\s*\[5\.\s*Additional Information\]", "additional_info")
    ]
    
    # 각 섹션 추출
    for i, (pattern, key) in enumerate(section_patterns):
        match = re.search(pattern, markdown_text, re.IGNORECASE)
        if match:
            start_idx = match.start()
            
            # 다음 섹션 찾기
            next_start = len(markdown_text)
            if i + 1 < len(section_patterns):
                next_pattern = section_patterns[i + 1][0]
                next_match = re.search(next_pattern, markdown_text, re.IGNORECASE)
                if next_match:
                    next_start = next_match.start()
            
            sections[key] = markdown_text[start_idx:next_start].strip()
    
    return sections


def validate_jrs_result(result: Dict[str, Any]) -> bool:
    """
    JRS 파싱 결과가 유효한지 검증
    
    필수 검증 항목:
    - min_rcs_level, target_rcs_level, jrs_markdown, parsed_data 존재
    - jrs_markdown 최소 길이 체크
    - parsed_data에 기본 섹션 존재
    """
    required_keys = ["min_rcs_level", "target_rcs_level", "jrs_markdown", "parsed_data"]
    
    # 필수 키 존재 여부 확인
    for key in required_keys:
        if key not in result:
            return False
    
    # jrs_markdown 최소 길이 확인 (너무 짧으면 파싱 실패로 간주)
    if len(result["jrs_markdown"]) < 200:
        return False
    
    # parsed_data 구조 확인
    parsed_data = result["parsed_data"]
    required_sections = ["basic_profile", "hard_skills", "soft_skills", "domain"]
    
    for section in required_sections:
        if section not in parsed_data:
            return False
    
    return True
