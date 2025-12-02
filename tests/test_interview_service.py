import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

# Import all models to ensure SQLAlchemy registry is populated
import src.models.user
import src.models.documnet
import src.models.interview
import src.models.vector_mapping

from src.services.interview_service.interview_service import process_interview_turn, get_latest_resume_summary
from src.models.interview import InterviewSession, ChatLog
from src.models.documnet import Resume

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_audio_file():
    file = MagicMock(spec=UploadFile)
    file.read = AsyncMock(return_value=b"audio data")
    return file

class TestInterviewService:
    def test_get_latest_resume_summary_found(self, mock_db):
        # Given
        user_id = 1
        mock_resume = Resume(jobseeker_id=user_id, brief_self_introduction="This is a summary of the resume.")
        
        # Mock DB query chain
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order_by = mock_filter.order_by.return_value
        mock_order_by.first.return_value = mock_resume

        # When
        summary = get_latest_resume_summary(mock_db, user_id)

        # Then
        assert "This is a summary" in summary

    def test_get_latest_resume_summary_not_found(self, mock_db):
        # Given
        user_id = 1
        
        # Mock DB query chain
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order_by = mock_filter.order_by.return_value
        mock_order_by.first.return_value = None

        # When
        summary = get_latest_resume_summary(mock_db, user_id)

        # Then
        assert "이력서 요약 데이터 없음" in summary

    @pytest.mark.asyncio
    async def test_process_interview_turn_success(self, mock_db, mock_audio_file):
        # Given
        session_id = "test_session_id"
        
        # Mock Session
        mock_session = InterviewSession(
            session_id=session_id, 
            user_id=1, 
            stage="GROWTH", 
            current_mode="MID",
            turn_count=0
        )
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_session

        # Mock ChatLog (Last question)
        mock_chat_log = ChatLog(id=1, session_id=session_id, ai_text="Last Question?")
        # We need to handle multiple queries. 
        # First query is for InterviewSession, Second is for ChatLog
        # It's easier to mock side_effect of filter_by or just mock the chain more carefully
        
        # Let's use side_effect for filter_by to distinguish calls if needed, 
        # but here they are different tables.
        # db.query(InterviewSession) -> ...
        # db.query(ChatLog) -> ...
        
        def query_side_effect(model):
            mock_q = MagicMock()
            if model == InterviewSession:
                mock_q.filter_by.return_value.first.return_value = mock_session
            elif model == ChatLog:
                mock_q.filter_by.return_value.order_by.return_value.first.return_value = mock_chat_log
            elif model == Resume:
                 mock_q.filter.return_value.order_by.return_value.first.return_value = Resume(brief_self_introduction="Resume Summary")
            return mock_q
            
        mock_db.query.side_effect = query_side_effect

        # Mock Agents
        with patch("src.services.interview_service.interview_service.interview_agent") as mock_agent:
            mock_agent.run_evaluator = AsyncMock(return_value={"action": "LEVEL_UP"})
            mock_agent.generate_reply = AsyncMock(return_value="AI Reply")

            # When
            result = await process_interview_turn(mock_db, session_id, mock_audio_file)

            # Then
            assert result["npc_text"] == "AI Reply"
            assert result["action"] == "LEVEL_UP"
            assert result["current_mode"] == "HIGH"
            assert mock_session.turn_count == 1
            assert mock_session.current_mode == "HIGH" # LEVEL_UP from MID -> HIGH

    @pytest.mark.asyncio
    async def test_process_interview_turn_session_not_found(self, mock_db, mock_audio_file):
        # Given
        session_id = "unknown_session"
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            await process_interview_turn(mock_db, session_id, mock_audio_file)
        
        assert exc_info.value.status_code == 404
