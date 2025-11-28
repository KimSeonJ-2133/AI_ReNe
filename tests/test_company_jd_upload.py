"""
기업 채용 공고 파일 업로드 및 JRS 파싱 기능 테스트
"""

import os
import pytest
from src.agents.tools.file_text_extractor import extract_text_from_file
from src.agents.company_jd_parser_agent import (
    parse_jd_with_llm,
    validate_jrs_result,
    parse_jrs_sections
)


# 테스트 픽스처: 채용 공고 샘플 파일 경로
@pytest.fixture(params=[
    "jd_backend_senior.txt",
    "jd_startup_fullstack.txt"
])
def jd_sample_file(request):
    """채용 공고 샘플 파일 경로 반환"""
    base_path = os.path.join(os.path.dirname(__file__), "fixtures")
    return os.path.join(base_path, request.param)


def test_extract_jd_text(jd_sample_file):
    """
    채용 공고 파일에서 텍스트 추출 테스트
    """
    # 파일에서 텍스트 추출
    text_content = extract_text_from_file(jd_sample_file)
    
    # 검증: 텍스트가 추출되었는지 확인
    assert text_content is not None
    assert len(text_content) > 100, "추출된 텍스트가 너무 짧습니다."
    
    print(f"\n[추출된 채용 공고 텍스트 길이: {len(text_content)} 글자]")
    print(f"파일: {os.path.basename(jd_sample_file)}")


def test_parse_jd_with_llm(jd_sample_file):
    """
    LLM을 사용하여 채용 공고를 JRS 포맷으로 파싱하는 테스트
    """
    # 1. 텍스트 추출
    text_content = extract_text_from_file(jd_sample_file)
    
    # 2. LLM 파싱
    result = parse_jd_with_llm(text_content = text_content, file_type = "text")
    
    # 3. 결과 검증
    assert "min_rcs_level" in result
    assert "target_rcs_level" in result
    assert "jrs_markdown" in result
    assert "parsed_data" in result
    
    # 4. RCS 레벨 형식 검증
    assert result["min_rcs_level"].startswith("Lv."), "Min RCS Level 형식이 올바르지 않습니다."
    assert result["target_rcs_level"].startswith("Lv."), "Target RCS Level 형식이 올바르지 않습니다."
    
    # 5. JRS 마크다운 길이 검증
    assert len(result["jrs_markdown"]) > 500, "JRS 마크다운이 너무 짧습니다."
    
    # 6. 파싱된 데이터 구조 검증
    parsed_data = result["parsed_data"]
    assert "basic_profile" in parsed_data
    assert "hard_skills" in parsed_data
    assert "soft_skills" in parsed_data
    assert "domain" in parsed_data
    
    # 7. 결과 출력
    print(f"\n[JRS 파싱 결과]")
    print(f"파일: {os.path.basename(jd_sample_file)}")
    print(f"Min RCS Level: {result['min_rcs_level']}")
    print(f"Target RCS Level: {result['target_rcs_level']}")
    print(f"JRS Markdown 길이: {len(result['jrs_markdown'])} 글자")
    
    # 8. JRS 마크다운을 파일로 저장
    output_filename = os.path.basename(jd_sample_file).replace(".txt", "_jrs_parsed.md")
    output_path = os.path.join(os.path.dirname(jd_sample_file), output_filename)
    
    with open(output_path, "w", encoding = "utf-8") as f:
        f.write(result["jrs_markdown"])
    
    print(f"JRS 파싱 결과 저장: {output_path}")


def test_validate_jrs_result():
    """
    JRS 파싱 결과 검증 함수 테스트
    """
    # 유효한 결과
    valid_result = {
        "min_rcs_level": "Lv.3",
        "target_rcs_level": "Lv.5",
        "jrs_markdown": "# [1. Basic Target Profile]\n..." * 50,  # 충분한 길이
        "parsed_data": {
            "basic_profile": "...",
            "hard_skills": "...",
            "soft_skills": "...",
            "domain": "..."
        }
    }
    
    assert validate_jrs_result(valid_result) == True
    
    # 필수 키 누락
    invalid_result_1 = {
        "min_rcs_level": "Lv.3",
        "target_rcs_level": "Lv.5"
        # jrs_markdown, parsed_data 누락
    }
    
    assert validate_jrs_result(invalid_result_1) == False
    
    # jrs_markdown이 너무 짧음
    invalid_result_2 = {
        "min_rcs_level": "Lv.3",
        "target_rcs_level": "Lv.5",
        "jrs_markdown": "Too short",
        "parsed_data": {
            "basic_profile": "...",
            "hard_skills": "...",
            "soft_skills": "...",
            "domain": "..."
        }
    }
    
    assert validate_jrs_result(invalid_result_2) == False
    
    print("[JRS 결과 검증 테스트 통과]")


def test_parsed_jrs_sections(jd_sample_file):
    """
    JRS 섹션 파싱 테스트
    """
    # 1. 텍스트 추출
    text_content = extract_text_from_file(jd_sample_file)
    
    # 2. LLM 파싱
    result = parse_jd_with_llm(text_content = text_content, file_type = "text")
    
    # 3. 섹션 파싱
    sections = parse_jrs_sections(result["jrs_markdown"])
    
    # 4. 각 섹션이 존재하는지 확인
    assert "basic_profile" in sections
    assert "hard_skills" in sections
    assert "soft_skills" in sections
    assert "domain" in sections
    
    # 5. 각 섹션이 비어있지 않은지 확인
    assert len(sections["basic_profile"]) > 50, "Basic Profile 섹션이 너무 짧습니다."
    assert len(sections["hard_skills"]) > 50, "Hard Skills 섹션이 너무 짧습니다."
    assert len(sections["soft_skills"]) > 50, "Soft Skills 섹션이 너무 짧습니다."
    assert len(sections["domain"]) > 50, "Domain 섹션이 너무 짧습니다."
    
    print(f"\n[JRS 섹션 파싱 결과]")
    print(f"파일: {os.path.basename(jd_sample_file)}")
    print(f"Basic Profile: {len(sections['basic_profile'])} 글자")
    print(f"Hard Skills: {len(sections['hard_skills'])} 글자")
    print(f"Soft Skills: {len(sections['soft_skills'])} 글자")
    print(f"Domain: {len(sections['domain'])} 글자")
