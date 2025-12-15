from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.services.stt_service.faster_whisper_service import FasterWhisperService
from src.models.interview import InterviewSession, ChatLog, ReneInterview
from src.models.user import Jobseeker
from src.models.document import Resume, Portfolio
from src.core.database import SessionLocal
from src.agents.p2p_auditor_agent import analyze_interview_transcript
from src.schemas.p2p_schemas.p2p_response_dto import P2PChunkResponseDto, P2PReportResponseDto
from src.services.p2p_service.buffer_manager import buffer_manager
from src.utils.audio_file_utils import pcm_to_wav_bytes
from src.utils.pdf_utils import generate_pdf_from_markdown
from datetime import datetime
import json


# Initialize STT Service
try:
    stt_service = FasterWhisperService()
except Exception as e:
    print(f"STT Service Initialization Failed: {e}")
    stt_service = None

# 단일 세션용 상수 ID
DEFAULT_SESSION_ID = "single_session_v1"

async def process_p2p_audio_chunk(
    audio_file: UploadFile, 
    speaker_role: str,
    username: str = None
) -> P2PChunkResponseDto:
    """
    [P2P] 오디오 청크를 받아 동적 버퍼링 및 STT 처리
    Args:
        username: 파일명에서 추출한 사용자 식별자 (예: jobplz)
    """
    session_id = DEFAULT_SESSION_ID
    
    # Username이 전달되면 BufferManager에 저장 (세션별 사용자 매핑)
    if username:
        buffer_manager.set_session_user(session_id, username)
    
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

async def finalize_p2p_interview() -> str:
    """
    [P2P] 인터뷰 종료 및 보고서 생성
    Returns:
        str: 생성된 PDF 보고서 파일 경로
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

    # 1. 구직자 프로필 구성 (DB 연동)
    # 세션에 저장된 username(email)을 가져와서 구직자 조회
    session_username = buffer_manager.get_session_user(session_id)
    
    candidate_profile = {
        "user_id": "Unknown",
        "name": "Unknown",
        "skills": [],
        "portfolio_markdown": "" 
    }
    
    db = SessionLocal()
    try:
        jobseeker = None
        if session_username:
            # 이메일(username)로 구직자 조회
            jobseeker = db.query(Jobseeker).filter(Jobseeker.email == session_username).first()
            if not jobseeker:
                print(f"[P2P Service] 해당 이메일의 구직자를 찾을 수 없습니다: {session_username}")
        else:
            # Fallback: 하드코딩된 ID (테스트용)
            target_jobseeker_id = 2
            jobseeker = db.query(Jobseeker).filter(Jobseeker.id == target_jobseeker_id).first()
            print(f"[P2P Service] 세션 유저 정보가 없어 기본 ID({target_jobseeker_id})로 조회합니다.")

        if jobseeker:
            candidate_profile["user_id"] = str(jobseeker.id)
            candidate_profile["name"] = jobseeker.name
            
            # 가장 최근 포트폴리오 및 이력서 조회
            portfolio = db.query(Portfolio).filter(Portfolio.jobseeker_id == jobseeker.id).order_by(Portfolio.created_at.desc()).first()
            resume = db.query(Resume).filter(Resume.jobseeker_id == jobseeker.id).order_by(Resume.created_at.desc()).first()
            
            # 구조화된 요약 생성
            summary_parts = []
            
            # 1. Skills (Portfolio 우선, 없으면 Resume)
            skills_list = []
            if portfolio and portfolio.main_skills:
                skills_list = portfolio.main_skills
            elif resume and resume.skills:
                skills_list = resume.skills
                
            if skills_list:
                # 문자열 리스트인 경우와 객체 리스트인 경우 모두 처리
                normalized_skills = []
                for s in skills_list:
                    if isinstance(s, str):
                        normalized_skills.append(s)
                    elif isinstance(s, dict):
                        normalized_skills.append(s.get("tech_keyword") or s.get("name") or str(s))
                
                summary_parts.append(f"# [Skills]\n- {', '.join(normalized_skills)}")
                
                # candidate_profile["skills"] 업데이트 (기존 로직 호환성 유지)
                # 문자열 리스트를 객체 형태로 변환하여 저장
                for s in normalized_skills:
                    candidate_profile["skills"].append({
                        "tech_keyword": s,
                        "current_level": 1, # 기본값
                        "context": ""
                    })

            # 2. Projects (Portfolio)
            if portfolio and portfolio.project_details:
                projects_str = ["# [Key Projects]"]
                for idx, proj in enumerate(portfolio.project_details, 1):
                    if isinstance(proj, dict):
                        name = proj.get("project_name", "Unknown Project")
                        role = proj.get("position", "")
                        desc = proj.get("description", "")
                        projects_str.append(f"{idx}. {name} ({role})\n   - {desc}")
                if len(projects_str) > 1:
                    summary_parts.append("\n".join(projects_str))

            # 3. Experience (Resume)
            if resume and resume.work_experience:
                exp_str = ["# [Experience]"]
                for idx, exp in enumerate(resume.work_experience, 1):
                    if isinstance(exp, dict):
                        company = exp.get("company_name", "Unknown Company")
                        role = exp.get("role", "")
                        period = exp.get("period", "")
                        exp_str.append(f"{idx}. {company} ({role}) | {period}")
                if len(exp_str) > 1:
                    summary_parts.append("\n".join(exp_str))
            
            # 4. Education (Resume)
            if resume and resume.education:
                edu_str = ["# [Education]"]
                for edu in resume.education:
                    edu_str.append(f"- {edu}")
                if len(edu_str) > 1:
                    summary_parts.append("\n".join(edu_str))

            # 요약본 저장 (없으면 기존 마크다운 사용)
            if summary_parts:
                candidate_profile["portfolio_summary"] = "\n\n".join(summary_parts)
                print(f"[P2P Service] 구조화된 요약 생성 완료 (길이: {len(candidate_profile['portfolio_summary'])})")
            elif portfolio and portfolio.markdown_content:
                candidate_profile["portfolio_summary"] = portfolio.markdown_content
                print("[P2P Service] 구조화된 데이터가 없어 원본 마크다운을 사용합니다.")
            else:
                candidate_profile["portfolio_summary"] = "No portfolio data available."

        else:
            print(f"[P2P Service] 구직자를 찾을 수 없습니다. (User ID: {target_jobseeker_id})")
            
    except Exception as e:
        print(f"[P2P Service] DB 조회 중 오류 발생: {e}")
    finally:
        db.close()
        
    # Fallback: 요약본이 없는 경우 더미 데이터
    if not candidate_profile.get("portfolio_summary"):
        print("[P2P Service] 포트폴리오 데이터를 가져오지 못해 더미 데이터를 사용합니다.")
        candidate_profile["portfolio_summary"] = """
# [Basic Information]
- **Name:** Unknown
- **Summary:** No portfolio data available.
"""
        # skills는 사용하지 않으므로 비워둠
        candidate_profile["skills"] = []

    print(f"[P2P Service] Candidate Profile Summary Length: {len(candidate_profile['portfolio_summary'])}")

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
        
        # 세션 데이터 정리 (파일 삭제)
        # buffer_manager.clear_session(session_id)

        return pdf_path

    # PDF 생성이 안된 경우 (예외 처리)
    raise HTTPException(status_code=500, detail="Failed to generate PDF report")

def reset_p2p_session():
    """
    [P2P] 세션 데이터 초기화 (새로운 면접 시작 전 호출)
    """
    session_id = DEFAULT_SESSION_ID
    buffer_manager.clear_session(session_id)
    print(f"[P2P Service] Session {session_id} has been reset.")