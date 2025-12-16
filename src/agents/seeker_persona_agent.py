from typing import List
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from services.rag_service import seeker_rag_service
from prompts.interview_prompts import SEEKER_INTERVIEWEE_PROMPT
from schemas.interview_schemas.interview_schemas import InterviewMessage
from core.config import settings
from core.database import SessionLocal
from models.document import Portfolio, Resume

class SeekerPersonaAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4.1", 
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )

    def generate_answer(self, 
                        resume_id: int, 
                        job_title: str, 
                        history: List[InterviewMessage]) -> str:
        """
        포트폴리오(Main Skills) 및 RAG(Project Details)를 기반으로 면접 답변을 생성합니다.
        """
        
        # 1. 검색 쿼리 결정
        query = "자기소개, 강점, 주요 경력"
        if history:
            last_message = history[-1]
            if last_message.role == "interviewer":
                query = last_message.content
        
        # 2. RAG Retrieval (이력서/포트폴리오 검색)
        docs = seeker_rag_service.search_similar(
            query=query,
            filter_metadata={"db_record_id": resume_id},
            k=3
        )
        retrieved_context = "\n\n".join([doc.page_content for doc in docs])
        if not retrieved_context:
            retrieved_context = "(관련 경험을 찾을 수 없습니다. 솔직하게 답변하십시오.)"

        # 3. DB에서 Main Skills 조회
        main_skills_context = ""
        with SessionLocal() as db:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                portfolio = db.query(Portfolio).filter(Portfolio.jobseeker_id == resume.jobseeker_id).order_by(Portfolio.created_at.desc()).first()
                if portfolio and portfolio.main_skills:
                    skills = portfolio.main_skills if isinstance(portfolio.main_skills, list) else []
                    skill_list = []
                    for skill in skills:
                        name = skill.get("name", "Unknown")
                        level = skill.get("ncs_level", 1)
                        skill_list.append(f"{name} (Lv.{level})")
                    main_skills_context = ", ".join(skill_list)
                else:
                    main_skills_context = "(등록된 핵심 기술이 없습니다.)"
            else:
                main_skills_context = "(지원자 정보를 찾을 수 없습니다.)"

        # 4. 프롬프트 구성
        system_prompt = SEEKER_INTERVIEWEE_PROMPT.format(
            job_title=job_title,
            main_skills_context=main_skills_context,
            retrieved_context=retrieved_context
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        # 대화 기록 추가
        # Seeker 입장에서는 Interviewer가 'Human'(상대방)이고, 자신이 'AI'
        for msg in history:
            if msg.role == "interviewer":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "interviewee":
                messages.append(AIMessage(content=msg.content))
                
        # 5. LLM 호출
        response = self.llm.invoke(messages)
        return response.content
