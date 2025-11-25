"""파일 업로드 및 파싱 테스트"""
import pytest
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agents.tools.file_text_extractor import extract_text_from_file, get_text_preview
from agents.seeker_file_upload_agent import parse_resume_with_llm, validate_parsing_result


# Fixtures
@pytest.fixture(params=[
    "resume_table_format.txt",
    "resume_freeform.txt",
    "portfolio_projects.txt"
])
def sample_file_path(request):
    """여러 샘플 파일 경로"""
    return str(PROJECT_ROOT / "tests" / "fixtures" / request.param)


@pytest.fixture
def sample_file_text(sample_file_path):
    """샘플 파일 텍스트"""
    return extract_text_from_file(sample_file_path)


# 테스트 1: 텍스트 추출
def test_extract_text_from_txt_file(sample_file_path):
    """TXT 파일에서 텍스트 추출 테스트"""
    text = extract_text_from_file(sample_file_path)
    
    # 검증
    assert text is not None
    assert len(text) > 0
    assert "김개발" in text
    
    print(f"\n✅ 텍스트 추출 성공!")
    print(f"  - 파일: {Path(sample_file_path).name}")
    print(f"  - 길이: {len(text)} 자")
    print(f"  - 미리보기:\n{get_text_preview(text, 300)}\n")


# 테스트 2: LLM 파싱
def test_parse_resume_with_llm(sample_file_path, sample_file_text):
    """LLM을 사용한 이력서 파싱 테스트"""
    file_type = "portfolio" if "portfolio" in sample_file_path else "resume"
    result = parse_resume_with_llm(sample_file_text, file_type = file_type)
    
    # 검증
    assert result is not None
    assert "ncs_level" in result
    assert "rcs_level" in result
    assert "markdown_content" in result
    assert "parsed_data" in result
    
    # 레벨 검증
    assert result["ncs_level"] != "Unknown"
    assert result["rcs_level"] != "Unknown"
    
    # Markdown 내용 검증
    markdown = result["markdown_content"]
    assert len(markdown) > 0
    assert "[Basic Information]" in markdown
    assert "[Summary: Level Inference]" in markdown
    assert "[Hard Facts: Education & Certifications]" in markdown
    assert "[History]" in markdown
    assert "[Portfolio & Tech Context]" in markdown
    
    # 파싱 결과를 파일로 저장
    input_filename = Path(sample_file_path).stem
    output_path = PROJECT_ROOT / "tests" / "fixtures" / f"{input_filename}_parsed.md"
    with open(output_path, 'w', encoding = 'utf-8') as f:
        f.write(markdown)
    
    print(f"\n✅ LLM 파싱 성공!")
    print(f"  - 입력 파일: {Path(sample_file_path).name}")
    print(f"  - NCS Level: {result['ncs_level']}")
    print(f"  - RCS Level: {result['rcs_level']}")
    print(f"  - Markdown 길이: {len(markdown)} 자")
    print(f"  - 저장 위치: {output_path}")
    print(f"\n📄 파싱된 Markdown 미리보기:\n")
    print("=" * 80)
    print(get_text_preview(markdown, 500))
    print("=" * 80)


# 테스트 3: 파싱 결과 검증
def test_validate_parsing_result(sample_file_path, sample_file_text):
    """파싱 결과 유효성 검증 테스트"""
    file_type = "portfolio" if "portfolio" in sample_file_path else "resume"
    result = parse_resume_with_llm(sample_file_text, file_type = file_type)
    
    is_valid = validate_parsing_result(result)
    
    assert is_valid is True
    print(f"\n✅ 파싱 결과 검증 성공! ({Path(sample_file_path).name})")


# 테스트 4: 특정 섹션 추출 확인
def test_parsed_sections(sample_file_path, sample_file_text):
    """파싱된 섹션별 데이터 확인"""
    file_type = "portfolio" if "portfolio" in sample_file_path else "resume"
    result = parse_resume_with_llm(sample_file_text, file_type = file_type)
    parsed_data = result["parsed_data"]
    
    # 각 섹션이 존재하는지 확인
    assert "basic_info" in parsed_data
    assert "summary" in parsed_data
    assert "hard_facts" in parsed_data
    assert "history" in parsed_data
    assert "portfolio" in parsed_data
    
    print(f"\n✅ 섹션 파싱 성공! ({Path(sample_file_path).name})")
    print(f"  - Basic Info: {len(parsed_data['basic_info'])} 자")
    print(f"  - Summary: {len(parsed_data['summary'])} 자")
    print(f"  - Hard Facts: {len(parsed_data['hard_facts'])} 자")
    print(f"  - History: {len(parsed_data['history'])} 자")
    print(f"  - Portfolio: {len(parsed_data['portfolio'])} 자")


# 실행 가이드
if __name__ == "__main__":
    print("=" * 80)
    print("파일 업로드 및 파싱 테스트")
    print("=" * 80)
    print("\n실행 방법:")
    print("  pytest tests/test_seeker_file_upload.py -v -s")
    print("\n개별 테스트 실행:")
    print("  pytest tests/test_seeker_file_upload.py::test_extract_text_from_txt_file -v -s")
    print("  pytest tests/test_seeker_file_upload.py::test_parse_resume_with_llm -v -s")
    print("=" * 80)
