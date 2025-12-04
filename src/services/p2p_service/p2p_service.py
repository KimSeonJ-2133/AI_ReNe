from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.services.stt_service.faster_whisper_service import FasterWhisperService
from src.models.interview import InterviewSession, ChatLog, ReneInterview
from src.models.user import Jobseeker
from src.models.document import Resume
from src.agents.p2p_auditor_agent import analyze_interview_transcript
from src.schemas.p2p_schemas.p2p_response_dto import P2PChunkResponseDto, P2PReportResponseDto
from src.services.p2p_service.buffer_manager import buffer_manager
from src.utils.audio_file_utils import pcm_to_wav_bytes
from src.utils.pdf_utils import generate_pdf_from_markdown
from datetime import datetime
import json
import os

# Initialize STT Service
try:
    stt_service = FasterWhisperService()
except Exception as e:
    print(f"STT Service Initialization Failed: {e}")
    stt_service = None

# 단일 세션용 상수 ID
DEFAULT_SESSION_ID = "single_session_v1"

async def process_p2p_audio_chunk(audio_file: UploadFile, speaker_role: str) -> P2PChunkResponseDto:
    """
    [P2P] 오디오 청크를 받아 동적 버퍼링 및 STT 처리
    """
    session_id = DEFAULT_SESSION_ID
    
    if not stt_service:
        raise HTTPException(status_code=500, detail="STT Service is not available")

    # Step A: 현재 버퍼 상태 확인 (마지막 화자)
    last_speaker = buffer_manager.get_last_speaker(session_id)
    
    # 오디오 데이터 읽기 (PCM)
    audio_bytes = await audio_file.read()
    
    # Step B: 화자가 동일하면 버퍼링 (STT 수행 X)
    if last_speaker == speaker_role:
        buffer_manager.append_audio(session_id, audio_bytes)
        return P2PChunkResponseDto(
            session_id=session_id,
            turn_number=0, # DB 제거로 인해 턴 카운트 추적 생략 (필요시 파일 기반 구현 가능)
            text="", # 버퍼링 중이므로 텍스트 없음
            status="buffered"
        )
    
    # Step C: 화자가 바뀌면 플러시 & 변환
    # 1. 이전 화자의 오디오 버퍼 처리
    if last_speaker is not None:
        buffered_audio = buffer_manager.read_and_clear_buffer(session_id)
        if buffered_audio:
            # PCM -> WAV 변환
            wav_bytes = pcm_to_wav_bytes(buffered_audio)
            transcribed_text = stt_service.transcribe(wav_bytes)
            if transcribed_text:
                buffer_manager.save_transcript(session_id, last_speaker, transcribed_text)
    
    # 2. 현재 화자의 오디오로 새 버퍼 시작
    buffer_manager.append_audio(session_id, audio_bytes)
    buffer_manager.update_last_speaker(session_id, speaker_role)
    
    return P2PChunkResponseDto(
        session_id=session_id,
        turn_number=0,
        text="", # 현재 청크는 버퍼링 시작됨
        status="buffered"
    )

async def finalize_p2p_interview() -> P2PReportResponseDto:
    """
    [P2P] 인터뷰 종료 및 보고서 생성
    """
    session_id = DEFAULT_SESSION_ID
    
    # 0. 남은 버퍼 강제 플러시 (Flush remaining buffer)
    last_speaker = buffer_manager.get_last_speaker(session_id)
    if last_speaker:
        buffered_audio = buffer_manager.read_and_clear_buffer(session_id)
        if buffered_audio:
            wav_bytes = pcm_to_wav_bytes(buffered_audio)
            transcribed_text = stt_service.transcribe(wav_bytes)
            if transcribed_text:
                buffer_manager.save_transcript(session_id, last_speaker, transcribed_text)

    # 1. 구직자 프로필 구성 (DB 제거로 인한 더미 데이터 사용)
    candidate_profile = {
        "user_id": "dummy_user_id",
        "name": "테스트구직자",
        "skills": [
            {"tech_keyword": "Python", "current_level": 3, "context": "Backend Development"},
            {"tech_keyword": "FastAPI", "current_level": 2, "context": "API Development"}
        ]
    }

    # 2. 전체 대화록 구성 (BufferManager에서 가져오기)
    full_transcript = buffer_manager.get_full_transcript(session_id)

    # 3. P2P Auditor Agent 호출
    try:
        analysis_result = analyze_interview_transcript(candidate_profile, full_transcript)
    except Exception as e:
        print(f"Agent Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    # 4. 결과 저장 (DB 제거로 인해 생략)
    
    # [PDF 생성] Human Report를 PDF로 변환하여 저장
    human_report_md = analysis_result.get("human_report", "")
    if human_report_md:
        pdf_filename = f"report_{session_id}.pdf"
        # data/p2p_sessions/{session_id} 폴더는 삭제되므로, 상위 폴더나 별도 결과 폴더에 저장
        # 여기서는 data/reports 폴더에 저장한다고 가정
        report_dir = "data/reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
            
        pdf_path = os.path.join(report_dir, pdf_filename)
        generate_pdf_from_markdown(human_report_md, pdf_path)
        print(f"PDF Report generated at: {pdf_path}")

    # 5. 응답 반환
    response = P2PReportResponseDto(
        session_id=session_id,
        thinking_process=analysis_result.get("thinking_process", ""),
        human_report=analysis_result.get("human_report", ""),
        update_data=analysis_result.get("update_data", {}),
        raw_response=analysis_result.get("raw_response")
    )

    # 세션 데이터 정리 (파일 삭제)
    buffer_manager.clear_session(session_id)

    return response