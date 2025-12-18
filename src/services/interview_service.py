import uuid
import sys
import os
from typing import Dict
from sqlalchemy.orm import Session

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from schemas.interview_schemas.interview_schemas import InterviewSessionState, InterviewMessage, InterviewResponse
from agents.company_persona_agent import CompanyPersonaAgent
from agents.seeker_persona_agent import SeekerPersonaAgent
from models.user import Company
from models.document import RecruitmentNotice

# In-memory session storage (추후 Redis 등으로 교체 권장)
active_sessions: Dict[str, InterviewSessionState] = {}

company_agent = CompanyPersonaAgent()
seeker_agent = SeekerPersonaAgent()

class InterviewService:
    def create_session(self, db: Session, jobseeker_id: int, company_id: int, jd_id: int, resume_id: int) -> str:
        """
        새로운 인터뷰 세션을 생성합니다.
        """
        session_id = str(uuid.uuid4())
        state = InterviewSessionState(
            session_id=session_id,
            jobseeker_id=jobseeker_id,
            company_id=company_id,
            jd_id=jd_id,
            resume_id=resume_id
        )
        active_sessions[session_id] = state
        print(f"[InterviewService] Session created: {session_id}")
        return session_id

    async def process_next_step(self, db: Session, session_id: str) -> InterviewResponse:
        """
        인터뷰의 다음 턴(질문 또는 답변)을 진행합니다.
        """
        state = active_sessions.get(session_id)
        if not state:
            raise ValueError("Session not found")
            
        if state.current_turn >= state.max_turns:
            state.status = "completed"
            return InterviewResponse(
                session_id=session_id,
                message="면접이 종료되었습니다.",
                current_turn=state.current_turn,
                is_finished=True
            )

        # Context 정보 조회
        company = db.query(Company).filter(Company.id == state.company_id).first()
        company_name = company.name if company else "Company"
        
        # JD에서 직무명 조회
        notice = db.query(RecruitmentNotice).filter(RecruitmentNotice.id == state.jd_id).first()
        job_title = "직무"
        if notice and notice.job_group:
            job_title = notice.job_group.name
        
        # 턴 결정 (마지막 메시지 기준)
        last_role = state.history[-1].role if state.history else None
        
        new_message = None
        
        if last_role is None or last_role == "interviewee":
            # Company's Turn (질문 생성)
            print(f"[InterviewService] Company Agent generating question... (Turn {state.current_turn + 1})")
            
            # 동기 호출 (추후 비동기로 전환 가능)
            question = company_agent.generate_question(
                jd_id=state.jd_id,
                resume_id=state.resume_id,
                company_name=company_name,
                job_title=job_title,
                history=state.history
            )
            new_message = InterviewMessage(role="interviewer", content=question)
            state.current_turn += 1 
            
        elif last_role == "interviewer":
            # Seeker's Turn (답변 생성)
            print(f"[InterviewService] Seeker Agent generating answer...")
            
            answer = seeker_agent.generate_answer(
                resume_id=state.resume_id,
                job_title=job_title,
                history=state.history
            )
            new_message = InterviewMessage(role="interviewee", content=answer)
            
        state.history.append(new_message)
        
        return InterviewResponse(
            session_id=session_id,
            message=new_message.content,
            current_turn=state.current_turn,
            is_finished=False
        )

interview_service = InterviewService()
