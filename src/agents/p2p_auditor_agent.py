"""
P2P 면접 로그 분석 Agent
CoT(Chain of Thought) 기반 역량 검증 시스템
"""
# TODO : 해당 면접자의 추천도 및 적정 연봉

import json
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.prompts.p2p_auditor_prompts import P2P_AUDITOR_SYSTEM_PROMPT


def analyze_interview_transcript(
    candidate_profile: Dict[str, Any],
    interview_transcript: str,
    model: str = "gpt-4.1"
) -> Dict[str, Any]:
    """
    P2P 면접 로그를 분석하여 구직자의 역량을 검증
    
    Args:
        candidate_profile: 구직자 프로필 정보
            {
                "user_id": str,
                "name": str,
                "skills": [
                    {
                        "tech_keyword": str,
                        "current_level": int,  # RCS Level (1-8)
                        "context": str
                    }
                ]
            }
        interview_transcript: P2P 면접 대화 로그 (전체 텍스트)
        model: 사용할 LLM 모델 (기본값: gpt-4.1)
        
    Returns:
        Dict containing:
            - thinking_process: CoT 추론 과정 (str)
            - human_report: 사람이 읽을 수 있는 분석 리포트 (str)
            - update_data: JSON 형식의 업데이트 데이터 (dict)
            - raw_response: LLM의 원본 응답 (str)
    """
    # LLM 초기화 (High-End 모델 사용, 논리적 일관성을 위해 낮은 temperature)
    llm = ChatOpenAI(
        model = model,
        temperature = 0.1,
        api_key = settings.OPENAI_API_KEY
    )
    
    # 사용자 프롬프트 생성
    user_prompt = construct_user_prompt(candidate_profile, interview_transcript)
    
    # LLM 호출
    messages = [
        {"role": "system", "content": P2P_AUDITOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm.invoke(messages)
    raw_response = response.content.strip()
    
    # 응답 파싱
    parsed_result = parse_auditor_response(raw_response)
    parsed_result["raw_response"] = raw_response
    
    return parsed_result


def construct_user_prompt(
    candidate_profile: Dict[str, Any],
    interview_transcript: str
) -> str:
    """
    P2P Auditor에게 전달할 사용자 프롬프트 생성
    
    Args:
        candidate_profile: 구직자 프로필
        interview_transcript: 면접 대화 로그
        
    Returns:
        구조화된 사용자 프롬프트 문자열
    """
    # 구직자 스킬 정보 포맷팅
    skills_info = []
    for skill in candidate_profile.get("skills", []):
        skill_text = f"- **{skill['tech_keyword']}:** RCS Lv.{skill['current_level']}"
        if skill.get("context"):
            skill_text += f" (Context: {skill['context']})"
        skills_info.append(skill_text)
    
    skills_section = "\n".join(skills_info) if skills_info else "- (No skills registered)"
    
    # 포트폴리오 요약 섹션 추가 (우선순위: Summary > Markdown)
    portfolio_content = candidate_profile.get("portfolio_summary") or candidate_profile.get("portfolio_markdown") or ""
    
    portfolio_section = ""
    if portfolio_content:
        portfolio_section = f"""
# Portfolio / Resume Context
The following is the structured summary of the candidate's portfolio/resume:

{portfolio_content}
"""

    prompt = f"""# Candidate Profile (Avatar)

**User ID:** {candidate_profile.get('user_id', 'Unknown')}
**Name:** {candidate_profile.get('name', 'Unknown')}

**Current Skill Levels:**
{skills_section}

{portfolio_section}

---

# Interview Transcript

{interview_transcript}

---

# Task
Analyze the above interview transcript using Chain of Thought reasoning.
Validate whether the candidate's current skill levels (Avatar) are accurate based on their performance in the interview.

Follow the three-part output format strictly:
1. [PART 1: THINKING PROCESS] - Your internal reasoning
2. [PART 2: HUMAN REPORT] - Summary in Korean for the user
3. [PART 3: UPDATE DATA] - JSON format with action recommendations

Begin your analysis now.
"""
    
    return prompt


def parse_auditor_response(raw_response: str) -> Dict[str, Any]:
    """
    LLM 응답을 파싱하여 세 부분으로 분리
    
    Args:
        raw_response: LLM의 원본 응답 텍스트
        
    Returns:
        {
            "thinking_process": str,
            "human_report": str,
            "update_data": dict
        }
    """
    result = {
        "thinking_process": "",
        "human_report": "",
        "update_data": {}
    }
    
    # PART 1: Thinking Process 추출
    thinking_match = re.search(
        r'\[PART 1:.*?THINKING PROCESS.*?\](.*?)(?=\[PART 2:|---|\Z)',
        raw_response,
        re.DOTALL | re.IGNORECASE
    )
    if thinking_match:
        result["thinking_process"] = thinking_match.group(1).strip()
    
    # PART 2: Human Report 추출
    report_match = re.search(
        r'\[PART 2:.*?HUMAN REPORT.*?\](.*?)(?=\[PART 3:|---|\Z)',
        raw_response,
        re.DOTALL | re.IGNORECASE
    )
    if report_match:
        result["human_report"] = report_match.group(1).strip()
    
    # PART 3: Update Data (JSON) 추출
    json_match = re.search(
        r'\[PART 3:.*?UPDATE DATA.*?\].*?```json\s*(.*?)\s*```',
        raw_response,
        re.DOTALL | re.IGNORECASE
    )
    
    if json_match:
        try:
            result["update_data"] = json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 에러 정보 저장
            result["update_data"] = {
                "error": "JSON parsing failed",
                "detail": str(e),
                "raw_json": json_match.group(1)
            }
    
    return result


def apply_audit_results(
    candidate_profile: Dict[str, Any],
    audit_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Audit 결과를 구직자 프로필에 반영
    
    Args:
        candidate_profile: 원본 구직자 프로필
        audit_results: analyze_interview_transcript() 결과
        
    Returns:
        업데이트된 구직자 프로필
    """
    updated_profile = candidate_profile.copy()
    
    # update_data에서 변경사항 추출
    updates = audit_results.get("update_data", {}).get("updates", [])
    
    for update in updates:
        tech_keyword = update.get("tech_keyword")
        action = update.get("action")
        detected_level = update.get("detected_limit_level")
        
        # 해당 스킬 찾기
        for skill in updated_profile.get("skills", []):
            if skill["tech_keyword"] == tech_keyword:
                # Action에 따라 레벨 업데이트
                if action == "UPGRADE":
                    skill["current_level"] = min(detected_level + 1, 8)  # 최대 Lv.8
                    skill["audit_note"] = f"Upgraded from Lv.{update.get('current_level')} based on interview performance"
                
                elif action == "DOWNGRADE":
                    skill["current_level"] = max(detected_level, 1)  # detected_level로 조정
                    skill["audit_note"] = f"Downgraded from Lv.{update.get('current_level')} due to skill gap"
                
                elif action == "MAINTAIN":
                    # 레벨 유지, 검증 완료 표시
                    skill["audit_note"] = f"Level Lv.{skill['current_level']} validated"
                
                # 검증 증거 추가
                skill["last_audit"] = {
                    "reason": update.get("reason"),
                    "evidence": update.get("evidence", {}),
                    "timestamp": "2025-11-27"  # 실제로는 datetime.now() 사용
                }
                
                break
    
    return updated_profile


def validate_audit_results(audit_results: Dict[str, Any]) -> bool:
    """
    Audit 결과의 유효성 검증
    
    Args:
        audit_results: analyze_interview_transcript() 결과
        
    Returns:
        유효하면 True, 아니면 False
    """
    required_keys = ["thinking_process", "human_report", "update_data"]
    
    # 필수 키 존재 여부 확인
    for key in required_keys:
        if key not in audit_results:
            return False
    
    # thinking_process와 human_report가 비어있지 않은지 확인
    if not audit_results["thinking_process"] or not audit_results["human_report"]:
        return False
    
    # update_data가 올바른 구조인지 확인
    update_data = audit_results["update_data"]
    if "error" in update_data:
        return False
    
    if "updates" not in update_data:
        return False
    
    # 각 update 항목이 필수 필드를 가지고 있는지 확인
    required_update_keys = ["tech_keyword", "action", "detected_limit_level", "reason"]
    for update in update_data.get("updates", []):
        for key in required_update_keys:
            if key not in update:
                return False
    
    return True
