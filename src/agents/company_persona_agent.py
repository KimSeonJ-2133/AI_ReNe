from typing import List
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from services.rag_service import company_rag_service
from prompts.interview_prompts import COMPANY_INTERVIEWER_PROMPT
from schemas.interview_schemas.interview_schemas import InterviewMessage
from core.config import settings
from core.database import SessionLocal
from models.document import Portfolio, Resume

class CompanyPersonaAgent:
    def __init__(self):
        # 면접관은 맥락 파악이 중요하므로 고성능 모델 사용 권장
        self.llm = ChatOpenAI(
            model="gpt-4.1", 
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )

    def generate_question(self, 
                          jd_id: int, 
                          resume_id: int,
                          company_name: str, 
                          job_title: str, 
                          history: List[InterviewMessage]) -> str:
        """
        JD RAG 및 지원자 포트폴리오(DB)를 기반으로 면접 질문을 생성합니다.
        """
        
        # 1. 검색 쿼리 결정
        jd_query = "채용 공고의 필수 자격 요건 및 우대 사항, 주요 업무"
        if history:
            last_message = history[-1]
            if last_message.role == "interviewee":
                jd_query = f"지원자 답변: {last_message.content} 와 관련된 직무 요건"
        
        # 2. RAG Retrieval (JD 검색)
        jd_docs = company_rag_service.search_similar(
            query=jd_query,
            filter_metadata={"db_record_id": jd_id},
            k=3
        )
        jd_context = "\n\n".join([doc.page_content for doc in jd_docs])
        if not jd_context:
            jd_context = "(채용 공고 내용을 불러올 수 없습니다. 일반적인 면접 질문을 진행하십시오.)"

        # 3. DB에서 포트폴리오 정보 조회 (Main Skills & Project Details)
        portfolio_context = ""
        with SessionLocal() as db:
            # resume_id로 Jobseeker 찾기 (Resume 테이블 경유)
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            portfolio = None

            if resume:
                # 해당 구직자의 최신 포트폴리오 조회
                portfolio = db.query(Portfolio).filter(Portfolio.jobseeker_id == resume.jobseeker_id).order_by(Portfolio.created_at.desc()).first()
            else:
                # Resume가 없으면 resume_id가 Portfolio ID일 수 있음
                portfolio = db.query(Portfolio).filter(Portfolio.id == resume_id).first()

            if portfolio:
                # Main Skills 포맷팅
                if portfolio.main_skills:
                    portfolio_context += "### [Main Skills]\n"
                    skills = portfolio.main_skills if isinstance(portfolio.main_skills, list) else []
                    for skill in skills:
                        name = skill.get("name", "Unknown")
                        level = skill.get("ncs_level", 1)
                        reasoning = skill.get("reasoning", "")
                        portfolio_context += f"- **{name} (Lv.{level})**: {reasoning}\n"
                
                # Project Details 포맷팅
                if portfolio.project_details:
                    portfolio_context += "\n### [Project Details]\n"
                    projects = portfolio.project_details if isinstance(portfolio.project_details, list) else []
                    for project in projects:
                        p_name = project.get("project_name", "")
                        p_role = project.get("position", "")
                        p_desc = project.get("description", "")
                        portfolio_context += f"#### {p_name} ({p_role})\n{p_desc}\n"
            elif resume:
                # 포트폴리오가 없으면 이력서 내용 사용
                portfolio_context = f"### [Resume Summary]\n{resume.markdown_content[:1000]}..."
            else:
                portfolio_context = "(지원자 정보를 찾을 수 없습니다.)"

        # 4. 프롬프트 구성
        system_prompt = COMPANY_INTERVIEWER_PROMPT.format(
            company_name=company_name,
            job_title=job_title,
            jd_context=jd_context,
            portfolio_context=portfolio_context
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        # 대화 기록 추가
        for msg in history:
            if msg.role == "interviewer":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "interviewee":
                messages.append(HumanMessage(content=msg.content))
                
        # 5. LLM 호출
        response = self.llm.invoke(messages)
        return response.content
