import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# 환경 변수 설정 (임포트 전에 설정해야 Settings 검증 통과)
os.environ["ELEVENLABS_API_KEY"] = "test_api_key"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3306"

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.services.stt_service.whisper_korean_stt_service import WhisperKoreanSTTService
from src.services.stt_service.whisper_large_stt_service import WhisperLargeV3Service

# ==========================================
# STT Service Tests
# ==========================================

@patch("src.services.stt_service.whisper_korean_stt_service.librosa.load")
@patch("src.services.stt_service.whisper_korean_stt_service.pipeline")
def test_whisper_korean_stt_service(mock_pipeline, mock_librosa_load):
    """
    WhisperKoreanSTTService 단위 테스트
    - Singleton 인스턴스 생성 확인
    - transcribe 메서드 호출 시 파이프라인 동작 확인
    """
    # Mock Pipeline 설정
    mock_pipe_instance = MagicMock()
    mock_pipe_instance.return_value = {"text": "안녕하세요 테스트입니다."}
    mock_pipeline.return_value = mock_pipe_instance

    # Mock librosa.load 설정
    # (audio_array, sample_rate) 반환
    mock_librosa_load.return_value = (MagicMock(), 16000)

    # 서비스 인스턴스 생성 (Singleton 초기화)
    # 주의: 이미 다른 곳에서 초기화되었을 수 있으므로 _instance를 리셋하거나 기존 것 사용
    WhisperKoreanSTTService._instance = None 
    service = WhisperKoreanSTTService()
    
    # Mock Audio Data
    audio_data = b"fake_audio_bytes"
    
    # transcribe 호출
    result = service.transcribe(audio_data)
    
    # 검증
    assert result == "안녕하세요 테스트입니다."
    # 파이프라인이 호출되었는지 확인 (실제로는 오디오 데이터를 임시파일로 저장하고 경로를 넘김)
    mock_pipe_instance.assert_called()

@patch("src.services.stt_service.whisper_large_stt_service.librosa.load")
@patch("src.services.stt_service.whisper_large_stt_service.pipeline")
@patch("src.services.stt_service.whisper_large_stt_service.AutoModelForSpeechSeq2Seq")
@patch("src.services.stt_service.whisper_large_stt_service.AutoProcessor")
def test_whisper_large_v3_service(mock_processor, mock_model, mock_pipeline, mock_librosa_load):
    """
    WhisperLargeV3Service 단위 테스트
    - Singleton 인스턴스 생성 확인
    - transcribe 메서드 호출 시 파이프라인 동작 확인
    """
    # Mock 설정
    mock_pipe_instance = MagicMock()
    mock_pipe_instance.return_value = {"text": "Hello World"}
    mock_pipeline.return_value = mock_pipe_instance
    
    # Mock librosa.load 설정
    mock_librosa_load.return_value = (MagicMock(), 16000)

    # 서비스 인스턴스 생성
    WhisperLargeV3Service._instance = None
    service = WhisperLargeV3Service()
    
    # Mock Audio Data
    audio_data = b"fake_audio_bytes"
    
    # transcribe 호출
    result = service.transcribe(audio_data)
    
    # 검증
    assert result == "Hello World"
    mock_pipe_instance.assert_called()
