import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.services.stt_service.whisper_korean_stt_service import WhisperKoreanSTTService
from src.services.file_upload_service.seeker_file_upload_service import process_file_upload
from src.services.file_upload_service.company_file_upload_service import process_company_file_upload
from src.core.config import settings
from fastapi import UploadFile

# Fixture Paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_RESUME = FIXTURES_DIR / "sample_resume.txt"
SAMPLE_JD = FIXTURES_DIR / "sample_jd.txt"
SAMPLE_AUDIO = FIXTURES_DIR / "sample_speech_ko.mp3"

@pytest.mark.integration
class TestIntegrationServices:
    
    def test_stt_service_integration(self):
        """
        STT Service Integration Test
        - Uses real audio file
        - Uses real Whisper model (if available) or mocks if model missing
        """
        # Check if model exists
        model_path = Path(settings.WHISPER_KOREAN_MODEL_PATH)
        
        if not model_path.exists() or not any(model_path.iterdir()):
            print(f"\n[WARNING] STT Model not found at {model_path}. Skipping real model test.")
            # Fallback: If model is missing, we can't test the REAL model.
            # But the user wants to know what's missing.
            # We will assert False to let the user know, OR we can try to use a default model if allowed.
            # For now, let's fail with a clear message if the user expects a real test.
            pytest.skip("STT Model not found. Please download 'whisper_large_v3_turbo_korean' to 'data/models/'")
            return

        # If model exists, run real inference
        service = WhisperKoreanSTTService()
        
        with open(SAMPLE_AUDIO, "rb") as f:
            audio_bytes = f.read()
            
        result = service.transcribe(audio_bytes)
        
        print(f"\n[STT Result] {result}")
        assert "안녕하세요" in result
        assert "김철수" in result

    @pytest.mark.asyncio
    async def test_seeker_file_upload_integration(self):
        """
        Seeker File Upload Integration Test
        - Uses real text file
        - Uses real OpenAI API
        """
        if not settings.OPENAI_API_KEY:
             pytest.skip("OPENAI_API_KEY not found.")

        # Mock DB and File Upload object (we only want to test the Logic + LLM part)
        mock_db = MagicMock()
        
        # Create a file-like object for UploadFile
        with open(SAMPLE_RESUME, "rb") as f:
            file_content = f.read()
            
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "sample_resume.txt"
        mock_file.file = MagicMock()
        mock_file.file.read.return_value = file_content
        
        # We need to mock 'save_uploaded_file' to return our fixture path directly
        # because we don't want to actually save to 'data/datasets/...' in test
        with patch("src.services.file_upload_service.seeker_file_upload_service.save_uploaded_file") as mock_save:
            mock_save.return_value = str(SAMPLE_RESUME)
            
            # Call Service
            # Note: This will call real 'extract_text_from_file' and real 'parse_resume_with_llm'
            try:
                result = await process_file_upload(
                    session_id="test_session_int",
                    file_type="resume",
                    file=mock_file,
                    user_id="test_user",
                    db=mock_db
                )
                
                print(f"\n[Seeker Upload Result] {result}")
                assert result.ncs_level is not None
                assert result.rcs_level is not None
                assert "김철수" in result.parsed_markdown
                
            except Exception as e:
                pytest.fail(f"Seeker Integration Test Failed: {e}")

    @pytest.mark.asyncio
    async def test_company_file_upload_integration(self):
        """
        Company File Upload Integration Test
        - Uses real text file
        - Uses real OpenAI API
        """
        if not settings.OPENAI_API_KEY:
             pytest.skip("OPENAI_API_KEY not found.")

        mock_db = MagicMock()
        
        with open(SAMPLE_JD, "rb") as f:
            file_content = f.read()
            
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "sample_jd.txt"
        mock_file.file = MagicMock()
        mock_file.file.read.return_value = file_content
        
        with patch("src.services.file_upload_service.company_file_upload_service.save_uploaded_file") as mock_save:
            mock_save.return_value = str(SAMPLE_JD)
            
            try:
                result = await process_company_file_upload(
                    user_id="test_company",
                    file=mock_file,
                    db=mock_db,
                    session_id="test_session_company",
                    file_type="jd"
                )
                
                print(f"\n[Company Upload Result] {result}")
                assert result.min_rcs_level is not None
                assert result.target_rcs_level is not None
                assert "백엔드" in result.jrs_markdown
                
            except Exception as e:
                pytest.fail(f"Company Integration Test Failed: {e}")
