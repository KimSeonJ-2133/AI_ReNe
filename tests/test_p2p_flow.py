import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.core.config import settings

# 환경 변수 설정 (Import 전에 수행해야 함)
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database import Base
from src.api.deps import get_db
from src.models.user import Jobseeker
from src.models.interview import InterviewSession
from src.models.document import Resume
from src.services.p2p_service.buffer_manager import buffer_manager
from datetime import date

# 테스트용 DB 설정 (SQLite Memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_p2p_flow.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 의존성 오버라이드
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # DB 생성
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 테스트 데이터 생성
    try:
        # 1. Jobseeker
        jobseeker = Jobseeker(
            name="테스트구직자",
            email="test_p2p_flow@example.com",
            password="hashed_password",
            phone="010-0000-0000",
            birthdate=date(1990, 1, 1),
            gender="Male",
            address="Seoul",
            verified_grade="NOT_VERIFIED"
        )
        db.add(jobseeker)
        db.commit()
        db.refresh(jobseeker)

        # 2. Resume
        resume = Resume(
            jobseeker_id=jobseeker.id,
            brief_self_introduction="안녕하세요, 백엔드 개발자입니다.",
            skills=["Python", "FastAPI", "AWS"],
            markdown_content="내용",
            ncs_level=1,
            rcs_level=1
        )
        db.add(resume)
        
        # 3. InterviewSession
        session_id = "test_session_p2p_flow_001"
        session = InterviewSession(
            session_id=session_id,
            user_id=jobseeker.id,
            stage="P2P",
            turn_count=0
        )
        db.add(session)
        db.commit()
        
        yield db, session_id
        
    finally:
        db.close()
        if os.path.exists("./test_p2p_flow.db"):
            try:
                os.remove("./test_p2p_flow.db")
            except:
                pass
        # 버퍼 폴더 정리
        buffer_manager.clear_session("test_session_p2p_flow_001")

@pytest.fixture(scope="module", autouse=True)
def mock_services():
    # STT Service Mock
    with patch("src.services.p2p_service.p2p_service.stt_service") as mock_stt:
        mock_stt.transcribe.return_value = "테스트 발화 내용입니다."
        
        # LLM / Agent Mock (finalize_p2p_interview 내부)
        with patch("src.services.p2p_service.p2p_service.analyze_interview_transcript") as mock_agent:
            mock_agent.return_value = {
                "thinking_process": "Thinking...",
                "human_report": "면접 결과 보고서입니다.",
                "update_data": {}
            }
            yield mock_stt, mock_agent

def test_p2p_audio_flow(test_db):
    db, session_id = test_db
    
    # 더미 PCM 데이터 (16k, 16bit, mono, 1초 분량 = 32000 bytes)
    dummy_pcm = b"\x00" * 32000
    
    # 1. User 발화 (Chunk 1) -> Buffered
    response = client.post(
        f"/api/v1/p2p/session/{session_id}/audio",
        files={"file": ("chunk1.pcm", dummy_pcm, "application/octet-stream")},
        data={"speaker_role": "User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "buffered"
    
    # 2. User 발화 (Chunk 2) -> Buffered (같은 화자)
    response = client.post(
        f"/api/v1/p2p/session/{session_id}/audio",
        files={"file": ("chunk2.pcm", dummy_pcm, "application/octet-stream")},
        data={"speaker_role": "User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "buffered"

    # 3. Interviewer 발화 (Chunk 3) -> Flush User & Buffer Interviewer
    response = client.post(
        f"/api/v1/p2p/session/{session_id}/audio",
        files={"file": ("chunk3.pcm", dummy_pcm, "application/octet-stream")},
        data={"speaker_role": "Interviewer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "buffered"
    
    # 검증: BufferManager에 User 텍스트가 저장되었는지 확인
    transcript = buffer_manager.get_full_transcript(session_id)
    print(f"\n[Transcript Check]:\n{transcript}")
    assert "User:" in transcript

    # 4. Report 생성 (Flush Interviewer)
    response = client.post(f"/api/v1/p2p/report?session_id={session_id}")
    # Note: report endpoint expects session_id as query param based on previous code? 
    # Let's check p2p_interview_api.py again.
    # It is: async def generate_p2p_report(session_id: str, ...) -> Query param by default in FastAPI if not in path
    
    assert response.status_code == 200
    report = response.json()
    
    print(f"\n[Final Report]:\n{report}")
    assert report["session_id"] == session_id
    
    # 최종 Transcript 확인 (Interviewer도 포함되어야 함)
    transcript = buffer_manager.get_full_transcript(session_id)
    assert "Interviewer:" in transcript
