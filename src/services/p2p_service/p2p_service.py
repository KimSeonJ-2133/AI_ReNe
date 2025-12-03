from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.services.stt_service.faster_whisper_service import FasterWhisperService
from src.models.interview import InterviewSession, ChatLog, ReneInterview
from src.models.user import Jobseeker
from src.models.document import Resume
from src.agents.p2p_auditor_agent import analyze_interview_transcript
from src.schemas.p2p_schemas.p2p_response_dto import P2PChunkResponseDto, P2PReportResponseDto
from datetime import datetime
import json

# Initialize STT Service
try:
    stt_service = FasterWhisperService()
except Exception as e:
    print(f"STT Service Initialization Failed: {e}")
    stt_service = None

async def process_p2p_audio_chunk(db: Session, session_id: str, audio_file: UploadFile, speaker_role: str) -> P2PChunkResponseDto:
    """
    [P2P] 오디오 청크를 받아 STT 처리 후 로그에 저장
    """
    if not stt_service:
        raise HTTPException(status_code=500, detail="STT Service is not available")

    session = db.query(InterviewSession).filter_by(session_id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # STT 변환
    audio_bytes = await audio_file.read()
    text = stt_service.transcribe(audio_bytes)

    if not text:
        return P2PChunkResponseDto(
            session_id=session_id, 
            turn_number=session.turn_count, 
            text="", 
            status="failed"
        )

    # ChatLog에 저장 (User Turn)
    # P2P 면접은 사용자의 발화만 기록될 수도 있고, 상대방(AI)의 발화가 있을 수도 있음.
    # 여기서는 사용자의 발화를 누적하는 로직을 사용.
    
    last_log = db.query(ChatLog).filter_by(session_id=session_id).order_by(ChatLog.turn_number.desc()).first()
    
    # 마지막 로그가 있고, AI 응답이 비어있다면(아직 턴이 안 끝남) 이어붙이기
    if last_log and not last_log.ai_text:
        last_log.user_text = (last_log.user_text or "") + " " + text
        current_turn = last_log.turn_number
    else:
        # 새로운 턴 시작
        session.turn_count += 1
        current_turn = session.turn_count
        new_log = ChatLog(
            session_id=session_id,
            turn_number=current_turn,
            user_text=text,
            ai_text=None 
        )
        db.add(new_log)
    
    db.commit()

    return P2PChunkResponseDto(
        session_id=session_id,
        turn_number=current_turn,
        text=text,
        status="success"
    )

async def finalize_p2p_interview(db: Session, session_id: str) -> P2PReportResponseDto:
    """
    [P2P] 인터뷰 종료 및 보고서 생성
    """
    session = db.query(InterviewSession).filter_by(session_id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. 구직자 프로필 구성
    jobseeker = db.query(Jobseeker).filter(Jobseeker.id == session.user_id).first()
    if not jobseeker:
        raise HTTPException(status_code=404, detail="Jobseeker not found")
    
    resume = db.query(Resume).filter(Resume.jobseeker_id == session.user_id).order_by(Resume.created_at.desc()).first()
    
    skills_data = []
    if resume and resume.skills:
        # Resume.skills가 JSON이라고 가정 (List[str] 또는 List[Dict])
        # 여기서는 간단히 처리
        raw_skills = resume.skills
        if isinstance(raw_skills, list):
            for s in raw_skills:
                if isinstance(s, str):
                    skills_data.append({"tech_keyword": s, "current_level": 1, "context": "From Resume"})
                elif isinstance(s, dict):
                    skills_data.append({
                        "tech_keyword": s.get("name", "Unknown"),
                        "current_level": s.get("level", 1),
                        "context": s.get("description", "")
                    })

    candidate_profile = {
        "user_id": str(jobseeker.id),
        "name": jobseeker.name,
        "skills": skills_data
    }

    # 2. 전체 대화록 구성
    logs = db.query(ChatLog).filter_by(session_id=session_id).order_by(ChatLog.turn_number).all()
    full_transcript = ""
    for log in logs:
        if log.user_text:
            full_transcript += f"User: {log.user_text}\n"
        if log.ai_text:
            full_transcript += f"Interviewer: {log.ai_text}\n"

    # 3. P2P Auditor Agent 호출
    try:
        analysis_result = analyze_interview_transcript(candidate_profile, full_transcript)
    except Exception as e:
        print(f"Agent Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    # 4. 결과 저장 (ReneInterview)
    # P2P 면접 결과를 저장할 적절한 컬럼 매핑
    # summary -> human_report
    # total_evaluation -> update_data
    
    rene_interview = ReneInterview(
        jobseeker_id=session.user_id,
        interview_type="P2P_PEER_REVIEW", # P2P 타입 명시
        full_transcript=full_transcript,
        summary=analysis_result.get("human_report", ""),
        end_time=datetime.now()
    )
    db.add(rene_interview)
    db.commit()
    
    # 5. 응답 반환
    return P2PReportResponseDto(
        session_id=session_id,
        thinking_process=analysis_result.get("thinking_process", ""),
        human_report=analysis_result.get("human_report", ""),
        update_data=analysis_result.get("update_data", {}),
        raw_response=analysis_result.get("raw_response")
    )