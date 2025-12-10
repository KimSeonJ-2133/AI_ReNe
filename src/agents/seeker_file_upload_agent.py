"""이력서/포트폴리오 파싱 AI 에이전트"""
import os
import sys
import re
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 프롬프트 임포트
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from prompts.seeker_file_upload_tool_prompts import (
    SEEKER_FILE_UPLOAD_SYSTEM_PROMPT as SYSTEM_PROMPT
)
from core.config import settings


def parse_resume_with_llm(text_content: str, file_type: str = "resume") -> Dict[str, Any]:
    """
    LLM을 사용하여 이력서/포트폴리오 텍스트를 구조화된 Markdown으로 파싱
    
    Args:
        text_content: 파일에서 추출한 텍스트
        file_type: 파일 타입 ("resume" 또는 "portfolio")
    
    Returns:
        Dict[str, Any]: 파싱 결과
            - ncs_level: NCS 레벨
            - rcs_level: RCS 레벨
            - markdown_content: 전체 마크다운 텍스트
            - parsed_data: 구조화된 데이터 (섹션별 추출)
    
    Raises:
        Exception: LLM 호출 실패 또는 파싱 실패 시
    """
    try:
        # LLM 초기화
        llm = ChatOpenAI(
            model = "gpt-4.1-mini",
            temperature = 0.1,
            api_key = settings.OPENAI_API_KEY
        )
        
        # 프롬프트 구성
        system_message = SystemMessage(content = SYSTEM_PROMPT)
        human_message = HumanMessage(
            content = f"아래는 {file_type} 파일에서 추출한 텍스트입니다. 정해진 Markdown 형식으로 파싱해주세요.\n\n{text_content}"
        )
        
        # LLM 호출
        print(f"[Agent] LLM 파싱 시작... (텍스트 길이: {len(text_content)} 자)")
        response = llm.invoke([system_message, human_message])
        
        markdown_output = response.content.strip()
        
        # Markdown 코드 블록 제거 (```markdown ... ``` 형태로 감싸져 있을 수 있음)
        markdown_output = re.sub(r'^```markdown\s*\n', '', markdown_output, flags = re.MULTILINE)
        markdown_output = re.sub(r'\n```\s*$', '', markdown_output, flags = re.MULTILINE)
        
        print(f"[Agent] LLM 파싱 완료! (출력 길이: {len(markdown_output)} 자)")
        
        # NCS/RCS 레벨 추출
        ncs_level = extract_ncs_level(markdown_output)
        rcs_level = extract_rcs_level(markdown_output)
        
        # 섹션별 데이터 파싱
        parsed_data = parse_markdown_sections(markdown_output)
        
        return {
            "ncs_level": ncs_level,
            "rcs_level": rcs_level,
            "markdown_content": markdown_output,
            "parsed_data": parsed_data
        }
    
    except Exception as e:
        print(f"[Agent Error] LLM 파싱 실패: {e}")
        raise Exception(f"이력서 파싱 중 오류 발생: {str(e)}")


def extract_ncs_level(markdown_text: str) -> str:
    """
    Markdown에서 NCS 레벨 추출
    
    Args:
        markdown_text: LLM이 생성한 마크다운 텍스트
    
    Returns:
        str: NCS 레벨 (예: "Lv. 4 (Analysis)")
    """
    pattern = r'\*\*NCS Level:\*\*\s*\*\*(.+?)\*\*'
    match = re.search(pattern, markdown_text)
    if match:
        return match.group(1).strip()
    return "Unknown"


def extract_rcs_level(markdown_text: str) -> str:
    """
    Markdown에서 RCS 레벨 추출
    
    Args:
        markdown_text: LLM이 생성한 마크다운 텍스트
    
    Returns:
        str: RCS 레벨 (예: "Lv. 4 Solver")
    """
    pattern = r'\*\*RCS Level:\*\*\s*\*\*(.+?)\*\*'
    match = re.search(pattern, markdown_text)
    if match:
        return match.group(1).strip()
    return "Unknown"


def parse_markdown_sections(markdown_text: str) -> Dict[str, Any]:
    """
    Markdown 텍스트를 섹션별로 파싱하고 구조화된 데이터를 추출
    
    Args:
        markdown_text: LLM이 생성한 마크다운 텍스트
    
    Returns:
        Dict[str, Any]: 섹션별 데이터 및 구조화된 정보
    """
    # 1. 섹션 텍스트 추출
    basic_info_text = extract_section(markdown_text, r'# \[Basic Information\](.*?)---', re.DOTALL)
    summary_text = extract_section(markdown_text, r'# \[Summary: Level Inference\](.*?)---', re.DOTALL)
    hard_facts_text = extract_section(markdown_text, r'# \[Hard Facts: Education & Certifications\](.*?)---', re.DOTALL)
    history_text = extract_section(markdown_text, r'# \[History\](.*?)---', re.DOTALL)
    portfolio_text = extract_section(markdown_text, r'# \[Portfolio & Tech Context\](.*?)$', re.DOTALL)
    
    # 2. 구조화된 데이터 추출
    skills = extract_skills(hard_facts_text)
    education = extract_education(hard_facts_text)
    certifications = extract_certifications(hard_facts_text)
    work_experience = extract_history(history_text)
    project_details = extract_portfolio(portfolio_text)
    
    # 3. 결과 구성
    parsed_data = {
        "basic_info": basic_info_text,
        "summary": summary_text,
        "hard_facts": hard_facts_text,
        "history": history_text,
        "portfolio": portfolio_text,
        
        # 구조화된 데이터 (DB 저장용)
        "skills": skills,           # Resume용
        "main_skills": skills,      # Portfolio용 (동일하게 사용)
        "education": education,
        "certifications": certifications,
        "work_experience": work_experience,
        "project_details": project_details,
        
        # 기타 필드 (필요 시 추가 파싱)
        "brief_self_introduction": extract_summary_line(basic_info_text),
        "brief_project_introduction": [], # 별도 섹션이 없으므로 빈 리스트
        "other_experience": [],
        "languages": []
    }
    
    return parsed_data


def extract_skills(text: str) -> list:
    """Hard Facts 섹션에서 스킬 추출"""
    skills = []
    # 패턴: - [{Category}] **{Tech1 / Tech2}**
    pattern = r'-\s*\[(.*?)\]\s*\*\*(.*?)\*\*'
    matches = re.findall(pattern, text)
    
    for category, tech_str in matches:
        # 슬래시(/)나 콤마(,)로 구분된 기술 분리
        techs = [t.strip() for t in re.split(r'[/,]', tech_str)]
        skills.extend(techs)
        
    return list(set(skills)) # 중복 제거


def extract_education(text: str) -> list:
    """Hard Facts 섹션에서 학력 추출"""
    education_list = []
    # 패턴: - **Education:** {Content}
    pattern = r'-\s*\*\*Education:\*\*\s*(.*)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        education_list.append(match.strip())
        
    return education_list


def extract_certifications(text: str) -> list:
    """Hard Facts 섹션에서 자격증 추출"""
    cert_list = []
    # 패턴: - **Certification:** {Content}
    pattern = r'-\s*\*\*Certification:\*\*\s*(.*)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        cert_list.append(match.strip())
        
    return cert_list


def extract_history(text: str) -> list:
    """History 섹션에서 경력 추출"""
    history_list = []
    # ## 1. {Company Name} 패턴으로 분리
    companies = re.split(r'## \d+\.\s+', text)
    
    for company_block in companies:
        if not company_block.strip():
            continue
            
        lines = company_block.strip().split('\n')
        company_name = lines[0].strip() # 첫 줄은 회사명 (split에 의해 제목이 내용에 포함됨? 아니면 split이 제목을 먹음?)
        
        # re.split을 쓰면 구분자가 사라지므로, finditer를 쓰는게 나을 수 있음.
        # 간단하게 구현:
        pass
    
    # 더 정확한 파싱을 위해 finditer 사용
    pattern = r'## \d+\.\s+(.*?)\n(.*?)(?=## \d+\.|$)'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        company_name = match.group(1).strip()
        content = match.group(2).strip()
        
        # Period, Role 추출
        period_match = re.search(r'-\s*\*\*Period:\*\*\s*(.*)', content)
        role_match = re.search(r'-\s*\*\*Role:\*\*\s*(.*)', content)
        
        history_list.append({
            "company_name": company_name,
            "period": period_match.group(1).strip() if period_match else "",
            "role": role_match.group(1).strip() if role_match else ""
        })
        
    return history_list


def extract_portfolio(text: str) -> list:
    """Portfolio 섹션에서 프로젝트 추출"""
    project_list = []
    pattern = r'## \d+\.\s+(.*?)\n(.*?)(?=## \d+\.|$)'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        project_name = match.group(1).strip()
        content = match.group(2).strip()
        
        # Position 추출
        position_match = re.search(r'-\s*\*\*Position:\*\*\s*(.*)', content)
        
        # Facts 추출 (간단히 텍스트로 저장)
        facts = []
        fact_matches = re.findall(r'-\s*\*\*Fact \d+.*?\*\*\s*(.*)', content)
        facts.extend([f.strip('"') for f in fact_matches])
        
        project_list.append({
            "project_name": project_name,
            "position": position_match.group(1).strip() if position_match else "",
            "description": "\n".join(facts)
        })
        
    return project_list


def extract_summary_line(text: str) -> str:
    """Basic Info에서 Summary 추출"""
    match = re.search(r'-\s*\*\*Summary:\*\*\s*"(.*?)"', text)
    if match:
        return match.group(1).strip()
    return ""


def extract_section(text: str, pattern: str, flags = 0) -> str:
    """
    정규식 패턴으로 섹션 추출
    
    Args:
        text: 전체 텍스트
        pattern: 정규식 패턴
        flags: 정규식 플래그
    
    Returns:
        str: 추출된 섹션 텍스트
    """
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1).strip()
    return ""


def validate_parsing_result(result: Dict[str, Any]) -> bool:
    """
    파싱 결과 검증
    
    Args:
        result: parse_resume_with_llm의 반환값
    
    Returns:
        bool: 유효한 결과인지 여부
    """
    required_keys = ["ncs_level", "rcs_level", "markdown_content"]
    
    for key in required_keys:
        if key not in result or not result[key]:
            print(f"[Validation Error] 필수 키 '{key}'가 없거나 비어있습니다.")
            return False
    
    # Markdown 최소 길이 검증
    if len(result["markdown_content"]) < 100:
        print(f"[Validation Error] Markdown 출력이 너무 짧습니다.")
        return False
    
    return True
