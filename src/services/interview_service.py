# FastAPI & Type Hints
from fastapi import UploadFile
from sqlalchemy.orm import Session

from agents.interview_agent import interview_agent
from models.interview import InterviewSession, ChatLog

# STT 모듈 임포트
# TTS 모튤 임포트


# Main Service Logic
# -----
async def process_interview_turn(db: Session, session_id: str, audio_file: UploadFile):
    """
    면접 1턴(Turn) 처리 프로세스: Audio -> STT -> Brain -> TTS -> Audio
    """
    # 세션 정보 로드
    session = db.query(InterviewSession).filter_by(session_id=session_id).first()
    if not session:
        # 세션이 없으면 새로 생성 (로직 생략)
        pass

    # [STT] 음성 -> 텍스트
    # user_text = await transcribe(audio_file)
    user_text = "임시 테스트 텍스트입니다."  # Mock

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
    if action == "LEVEL_UP":
        if session.current_mode == "MID":
            session.current_mode = "HIGH"
        elif session.current_mode == "LOW":
            session.current_mode = "MID"
    elif action == "LEVEL_DOWN":
        if session.current_mode == "MID":
            session.current_mode = "LOW"
        elif session.current_mode == "HIGH":
            session.current_mode = "MID"

    # [Persona] 답변 생성
    persona_file = "ReNe of Growth.md"  # 로직에 따라 파일 선택

    # 프롬프트 변수 준비
    input_vars = {
        "current_mode": session.current_mode,
        "resume_summary": "DB에서 로드한 요약...",
        "previous_user_answer": user_text,  # High 모드
    }

    npc_text = await interview_agent.generate_reply(
        persona_file=persona_file,
        user_text=user_text,
        input_vars=input_vars,
        chat_history=[],  # 필요 시 DB에서 최근 2개 로드해서 주입
    )

    # [DB] 대화 로그 저장
    new_log = ChatLog(
        session_id=session_id,
        user_text=user_text,
        ai_text=npc_text,
        eval_score=eval_result.get("score"),
        eval_action=action,
    )
    db.add(new_log)
    db.commit()

    # [TTS] 음성 변환 및 리턴
    # audio_data= await generate(npc_text)

    return {
        "npc_text": npc_text,
        "current_mode": session.current_mode,
        "action": action,
    }
