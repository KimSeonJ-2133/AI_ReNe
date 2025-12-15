"""
P2P Auditor 기능 테스트
CoT 기반 역량 검증 시스템
"""

import os
import json
import pytest
from src.agents.p2p_auditor_agent import (
    analyze_interview_transcript,
    parse_auditor_response,
    apply_audit_results,
    validate_audit_results
)


# 테스트 픽스처: 구직자 프로필
@pytest.fixture
def sample_candidate_profile():
    """샘플 구직자 프로필"""
    return {
        "user_id": "user_12345",
        "name": "김철수",
        "skills": [
            {
                "tech_keyword": "JPA",
                "current_level": 3,
                "context": "Spring Boot 프로젝트에서 엔티티 설계 및 쿼리 작성"
            },
            {
                "tech_keyword": "Spring Framework",
                "current_level": 3,
                "context": "@Transactional, DI/IoC 패턴 활용"
            },
            {
                "tech_keyword": "Docker",
                "current_level": 3,
                "context": "개발 환경 구성용 Docker Compose 사용"
            }
        ]
    }


# 테스트 픽스처: 면접 로그
@pytest.fixture
def sample_interview_transcript():
    """샘플 P2P 면접 로그"""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "p2p_interview_sample_1.txt"
    )
    
    with open(fixture_path, "r", encoding = "utf-8") as f:
        return f.read()


def test_analyze_interview_transcript(sample_candidate_profile, sample_interview_transcript):
    """
    전체 P2P Auditor 분석 프로세스 테스트
    (실제 LLM 호출 포함)
    """
    # 분석 실행
    result = analyze_interview_transcript(
        candidate_profile = sample_candidate_profile,
        interview_transcript = sample_interview_transcript,
        model = "gpt-4.1"
    )
    
    # 결과 검증
    assert "thinking_process" in result
    assert "human_report" in result
    assert "update_data" in result
    assert "raw_response" in result
    
    # Thinking Process가 비어있지 않은지 확인
    assert len(result["thinking_process"]) > 100, "Thinking Process가 너무 짧습니다."
    
    # Human Report가 한국어로 작성되었는지 확인 (간단한 검증)
    assert "레벨" in result["human_report"] or "수준" in result["human_report"]
    
    # Update Data 구조 확인
    assert "updates" in result["update_data"]
    assert isinstance(result["update_data"]["updates"], list)
    
    # 출력
    print("\n" + "="*80)
    print("[THINKING PROCESS]")
    print("="*80)
    print(result["thinking_process"])
    
    print("\n" + "="*80)
    print("[HUMAN REPORT]")
    print("="*80)
    print(result["human_report"])
    
    print("\n" + "="*80)
    print("[UPDATE DATA]")
    print("="*80)
    print(json.dumps(result["update_data"], indent = 2, ensure_ascii = False))
    
    # 결과를 파일로 저장
    output_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "p2p_audit_result_sample_1.json"
    )
    
    with open(output_path, "w", encoding = "utf-8") as f:
        json.dump(result, f, indent = 2, ensure_ascii = False)
    
    print(f"\n분석 결과 저장: {output_path}")


def test_parse_auditor_response():
    """
    LLM 응답 파싱 로직 테스트
    """
    mock_response = """
[PART 1: THINKING PROCESS]
**Transcript Analysis:**
- Interviewer Q1: "Explain JPA Dirty Checking."
  - **Question Level:** Lv.3

- Candidate A1: "Dirty Checking is when JPA automatically detects changes..."
  - **Quality:** PASS

[PART 2: HUMAN REPORT]
## 검증 결과 요약

### 1. JPA (현재 레벨: Lv.3 Player)
현재 RCS Lv.3 수준이 적정합니다.

[PART 3: UPDATE DATA]
```json
{
  "updates": [
    {
      "tech_keyword": "JPA",
      "current_level": 3,
      "detected_limit_level": 3,
      "action": "MAINTAIN",
      "reason": "Successfully defended Lv.3 questions."
    }
  ]
}
```
"""
    
    result = parse_auditor_response(mock_response)
    
    # 검증
    assert "thinking_process" in result
    assert "human_report" in result
    assert "update_data" in result
    
    assert "Transcript Analysis" in result["thinking_process"]
    assert "검증 결과 요약" in result["human_report"]
    assert "updates" in result["update_data"]
    assert result["update_data"]["updates"][0]["tech_keyword"] == "JPA"
    
    print("\n[파싱 결과]")
    print(f"Thinking Process 길이: {len(result['thinking_process'])} 글자")
    print(f"Human Report 길이: {len(result['human_report'])} 글자")
    print(f"Update Data: {json.dumps(result['update_data'], ensure_ascii = False)}")


def test_apply_audit_results(sample_candidate_profile):
    """
    Audit 결과를 프로필에 반영하는 로직 테스트
    """
    mock_audit_results = {
        "thinking_process": "...",
        "human_report": "...",
        "update_data": {
            "updates": [
                {
                    "tech_keyword": "JPA",
                    "current_level": 3,
                    "detected_limit_level": 3,
                    "action": "MAINTAIN",
                    "reason": "Performance matches current level.",
                    "evidence": {
                        "passed_questions": ["Dirty Checking (Lv.3)", "N+1 Problem (Lv.4)"],
                        "failed_questions": ["OSIV (Lv.5)"],
                        "question_count": 3
                    }
                },
                {
                    "tech_keyword": "Spring Framework",
                    "current_level": 3,
                    "detected_limit_level": 2,
                    "action": "DOWNGRADE",
                    "reason": "Failed to explain propagation options (Lv.3 question).",
                    "evidence": {
                        "passed_questions": ["@Transactional basic (Lv.2)"],
                        "failed_questions": ["Propagation options (Lv.3)"],
                        "question_count": 2
                    }
                }
            ]
        }
    }
    
    # 결과 반영
    updated_profile = apply_audit_results(sample_candidate_profile, mock_audit_results)
    
    # 검증
    jpa_skill = next(s for s in updated_profile["skills"] if s["tech_keyword"] == "JPA")
    spring_skill = next(s for s in updated_profile["skills"] if s["tech_keyword"] == "Spring Framework")
    
    # JPA는 MAINTAIN이므로 레벨 유지
    assert jpa_skill["current_level"] == 3
    assert "validated" in jpa_skill["audit_note"]
    
    # Spring은 DOWNGRADE이므로 레벨 감소
    assert spring_skill["current_level"] == 2  # 3 -> 2
    assert "Downgraded" in spring_skill["audit_note"]
    
    # 검증 증거 확인
    assert "last_audit" in jpa_skill
    assert "evidence" in jpa_skill["last_audit"]
    
    print("\n[업데이트된 프로필]")
    print(json.dumps(updated_profile, indent = 2, ensure_ascii = False))


def test_validate_audit_results():
    """
    Audit 결과 유효성 검증 테스트
    """
    # 유효한 결과
    valid_result = {
        "thinking_process": "Some reasoning here...",
        "human_report": "검증 결과입니다...",
        "update_data": {
            "updates": [
                {
                    "tech_keyword": "JPA",
                    "action": "MAINTAIN",
                    "detected_limit_level": 3,
                    "reason": "Performance matches level."
                }
            ]
        }
    }
    
    assert validate_audit_results(valid_result) == True
    
    # 무효한 결과 (thinking_process 누락)
    invalid_result_1 = {
        "human_report": "검증 결과입니다...",
        "update_data": {"updates": []}
    }
    
    assert validate_audit_results(invalid_result_1) == False
    
    # 무효한 결과 (JSON 파싱 에러)
    invalid_result_2 = {
        "thinking_process": "...",
        "human_report": "...",
        "update_data": {
            "error": "JSON parsing failed"
        }
    }
    
    assert validate_audit_results(invalid_result_2) == False
    
    # 무효한 결과 (필수 필드 누락)
    invalid_result_3 = {
        "thinking_process": "...",
        "human_report": "...",
        "update_data": {
            "updates": [
                {
                    "tech_keyword": "JPA",
                    "action": "MAINTAIN"
                    # detected_limit_level, reason 누락
                }
            ]
        }
    }
    
    assert validate_audit_results(invalid_result_3) == False
    
    print("\n[검증 테스트 통과]")
