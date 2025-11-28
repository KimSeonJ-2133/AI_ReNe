import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

# Import all models to ensure SQLAlchemy registry is populated
import src.models.user
import src.models.documnet
import src.models.interview
import src.models.vector_mapping

from src.services.auth_service.auth_service import AuthService
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.jobseeker_schemas.jobseeker_response_dto import JobseekerSignupResponseDto, JobseekerLoginResponseDto
from src.models.user import Jobseeker

def test_signup_jobseeker_success():
    # Mock DB Session
    mock_db = MagicMock(spec=Session)
    
    # Mock Repository
    auth_service = AuthService(mock_db)
    auth_service.jobseeker_repo.get_by_email = MagicMock(return_value=None)
    
    mock_user = Jobseeker(id=1, email="test@example.com", name="Test User")
    auth_service.jobseeker_repo.create = MagicMock(return_value=mock_user)
    
    # Request DTO
    request = JobseekerSignupRequestDto(
        email="test@example.com",
        password="password123",
        name="Test User",
        phone="010-1234-5678",
        birthdate="1990-01-01",
        gender="Male",
        address="Seoul",
        policy_agree_bool=True
    )
    
    # Call Service
    response = auth_service.signup_jobseeker(request)
    
    # Verify Response
    assert isinstance(response, JobseekerSignupResponseDto)
    assert response.user_id == 1
    assert response.email == "test@example.com"
    assert response.message == "회원가입이 완료되었습니다."

def test_login_jobseeker_success():
    # Mock DB Session
    mock_db = MagicMock(spec=Session)
    
    # Mock Repository
    auth_service = AuthService(mock_db)
    
    mock_user = Jobseeker(id=1, email="test@example.com", name="Test User", password="password123")
    auth_service.jobseeker_repo.get_by_email = MagicMock(return_value=mock_user)
    
    # Request DTO
    request = JobseekerLoginRequestDto(
        email="test@example.com",
        password="password123"
    )
    
    # Call Service
    response = auth_service.login_jobseeker(request)
    
    # Verify Response
    assert isinstance(response, JobseekerLoginResponseDto)
    assert response.user_id == 1
    assert response.email == "test@example.com"
    assert response.name == "Test User"
    assert response.message == "로그인 성공"
