import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Set dummy API key before imports to avoid OpenAIError during module loading
os.environ["OPENAI_API_KEY"] = "dummy"

# Add src to path so we can import modules as top-level
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from services.interview_service import interview_service
from models.user import Company, JobGroup
from models.document import RecruitmentNotice

@pytest.mark.asyncio
async def test_interview_simulation_flow():
    # Mock DB
    mock_db = MagicMock()
    mock_company = Company(id=1, name="Test Corp")
    mock_job_group = JobGroup(id=1, name="Python Developer")
    mock_notice = RecruitmentNotice(id=1, job_group=mock_job_group)
    
    # DB query mocking is tricky because it's chained.
    # We'll mock the return values of the chain.
    # query() -> filter() -> first()
    
    # We need to handle multiple calls.
    # 1st call: Company
    # 2nd call: RecruitmentNotice
    # 3rd call: Company (next step)
    # 4th call: RecruitmentNotice (next step)
    
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.side_effect = [
        mock_company, mock_notice,
        mock_company, mock_notice
    ]

    # Mock Agents to avoid real LLM calls
    # Note: We must patch the module where it is used. 
    # Since we imported 'services.interview_service', we patch 'services.interview_service.company_agent'
    with patch("services.interview_service.company_agent") as mock_company_agent, \
         patch("services.interview_service.seeker_agent") as mock_seeker_agent:
        
        mock_company_agent.generate_question.return_value = "자기소개 부탁드립니다."
        mock_seeker_agent.generate_answer.return_value = "저는 파이썬 개발자입니다."
        
        # 1. Create Session
        session_id = interview_service.create_session(mock_db, 1, 1, 1, 1)
        assert session_id is not None
        
        print(f"\n[Test] Session Created: {session_id}")
        
        # 2. Step 1: Company asks question
        print("[Test] Step 1: Company Turn")
        response1 = await interview_service.process_next_step(mock_db, session_id)
        print(f"  -> Message: {response1.message}")
        assert response1.message == "자기소개 부탁드립니다."
        assert response1.current_turn == 1
        
        # 3. Step 2: Seeker answers
        print("[Test] Step 2: Seeker Turn")
        response2 = await interview_service.process_next_step(mock_db, session_id)
        print(f"  -> Message: {response2.message}")
        assert response2.message == "저는 파이썬 개발자입니다."
        assert response2.current_turn == 1 
        
        print("\n[Success] Interview simulation flow verified.")
