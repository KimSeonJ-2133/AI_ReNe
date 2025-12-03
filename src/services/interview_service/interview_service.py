#모듈 정의 : AI 면접 진행(STT -> Brain -> TTS) 및 세션 관리 - Service Module
#연결 모듈 : src/api/endpoints/rene_interview_api.py (API),
#  src/agents/interview_agent.py (Agent)
# FastAPI & Type Hints
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from src.agents.interview_agent import interview_agent
from src.models.interview import InterviewSession, ChatLog
from src.models.document import Resume, Portfolio

# STT 모듈 임포트
# TTS 모튤 임포트


# Main Service Logic
# -----
def get_latest_resume_summary(db: Session, user_id: int) -> str:
    """DB에서 최신 이력서 요약(parsed_markdown)을 로드합니다."""
    # 실제 구현 시, 최신 Resume/Portfolio 레코드를 찾아서 필요한 정보를 추출해야 합니다.
    # 현재는 Mocking 하며 DB 세션 사용 구조만 보여줍니다.
    latest_doc = db.query(Resume).filter(Resume.jobseeker_id == user_id).order_by(Resume.created_at.desc()).first()
    if latest_doc and latest_doc.brief_self_introduction:
        return latest_doc.brief_self_introduction[:300] + "..."
    return "이력서 요약 데이터 없음. 기본 프로필을 사용합니다."

async def process_interview_turn(db: Session, session_id: str, audio_file: UploadFile):
    """
    면접 1턴(Turn) 처리 프로세스: Audio -> STT -> Brain -> TTS -> Audio
    """
    # 세션 정보 로드
    session = db.query(InterviewSession).filter_by(session_id=session_id).first()
    if not session:
        # 세션이 없으면 새로 생성 (로직 생략)
        raise HTTPException(status_code= 404, detail= "면접 세션을 찾을 수 없습니다.")
    
    try:
        # [STT] 음성 -> 텍스트
        # user_text = stt_service.trascribe(await audio_file.read())
        user_text = "사용자 음성 인식을 대체하는 임시 테스트 텍스트입니다."     # Mock

        # [Logic] 구직자 프로필 로드
        resume_summary = get_latest_resume_summary(db, session.user_id)     

        # [Evaluator] 평가
        context_type = "SKILL_CHECK" if session.stage == "GROWTH" else "INFO_GATHERING"

        # 직접 질문 가져오기 (DB에서 조회)
        last_log = (
            db.query(ChatLog)
            .filter_by(session_id=session_id)
            .order_by(ChatLog.id.desc())
            .first()
        )
        last_question = last_log.ai_text if last_log else "첫 질문입니다."

        eval_result = await interview_agent.run_evaluator(
            context_type=context_type, question=last_question, answer=user_text
        )

        # [Logic] 모드 변경 및 DB 업데이트
        action = eval_result.get("action")
        new_mode = session.current_mode

        if session.stage == "GROWTH" or session.stage == "TRIAL":
            # Universal_Evaluator.md의 Action (LEVEL_UP/STAY/LEVEL_DOWN)에 따라 모든 변경
            if action == "LEVEL_UP":
                if session.current_mode == "MID":
                    new_mode = "HIGH"
                elif session.current_mode == "LOW":
                    new_mode = "MID"
            elif action == "LEVEL_DOWN":
                if session.current_mode == "MID":
                    new_mode = "LOW"
                elif session.current_mode == "HIGH":
                    new_mode = "MID"
        session.current_mode = new_mode     
        session.turn_count += 1
        # session.current_rcs_level = ...       # (TODO: RCS 레벨 업데이트 로직 추가)

        # [Persona] 답변 생성
        if session.stage == "GROWTH":
            persona_file = "ReNe of Growth.md"          # 로직에 따라 파일 선택
        elif session.stage == "TRIAL":
            persona_file = "Corperate_Recruiter.md"     # (TODO: JRS 데이터 주입 로직 추가 필요)
        else:
            persona_file = "ReNe_of_the_Beginning.md"

        # 프롬프트 변수 준비
        input_vars = {
            "current_mode": session.current_mode,
            "resume_summary": resume_summary,
            "previous_user_answer": user_text,  # High 모드
            "user_text": user_text              # HumanMessage에 포함되므로 중복될 수 있으나, Persona 파일에서 사용될 경우를 위해 추가
        }

        # (TODO: chat_history 로딩 로직 추가)
        npc_text = await interview_agent.generate_reply(
            persona_file=persona_file,
            user_text=user_text,
            input_vars=input_vars,
            chat_history=[],  # 필요 시 DB에서 최근 2개 로드해서 주입
        )

        # [DB] 대화 로그 저장
        new_log = ChatLog(
            session_id=session_id,
            turn_number=session.turn_count, 
            user_text=user_text,
            ai_text=npc_text,
            eval_score=eval_result.get("score"),
            eval_action=action,
        )
        db.add(new_log)
        db.add(session)
        db.commit()

        # [TTS] 음성 변환 및 리턴
        # audio_data= await generate(npc_text)

        return {
            "npc_text": npc_text,
            "current_mode": session.current_mode,
            "action": action,
            "turn_count": session.turn_count
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code= 500, detail= f"면접 처리 중 오류 발생: {str(e)}")
