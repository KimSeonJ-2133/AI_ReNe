import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Import all models to ensure SQLAlchemy registry is populated
import src.models.user
import src.models.document
import src.models.interview
import src.models.vector_mapping

from src.services.auth_service.auth_service import AuthService
from src.schemas.jobseeker_schemas.jobseeker_request_dto import JobseekerSignupRequestDto, JobseekerLoginRequestDto
from src.schemas.company_schemas.company_request_dto import CompanySignupRequestDto, CompanyLoginRequestDto
from src.models.user import Jobseeker, Company

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def auth_service(mock_db):
    with patch("src.services.auth_service.auth_service.JobseekerRepository") as MockJobseekerRepo, \
         patch("src.services.auth_service.auth_service.CompanyRepository") as MockCompanyRepo:
        
        service = AuthService(mock_db)
        service.jobseeker_repo = MockJobseekerRepo.return_value
        service.company_repo = MockCompanyRepo.return_value
        return service

class TestAuthService:
    def test_signup_jobseeker_success(self, auth_service):
        # Given
        request = JobseekerSignupRequestDto(
            email="test@example.com",
            password="password123",
            name="Test User",
            phone="010-1234-5678",
            birthdate="1990-01-01",
            gender="M",
            address="Seoul",
            policy_agree_bool=True
        )
        
        auth_service.jobseeker_repo.get_by_email.return_value = None
        
        mock_user = Jobseeker(id=1, email="test@example.com", name="Test User")
        auth_service.jobseeker_repo.create.return_value = mock_user

        # When
        response = auth_service.signup_jobseeker(request)

        # Then
        assert response.email == "test@example.com"
        assert response.user_id == 1
        auth_service.jobseeker_repo.create.assert_called_once()

    def test_signup_jobseeker_duplicate_email(self, auth_service):
        # Given
        request = JobseekerSignupRequestDto(
            email="duplicate@example.com",
            password="password123",
            name="Test User",
            phone="010-1234-5678",
            birthdate="1990-01-01",
            gender="M",
            address="Seoul",
            policy_agree_bool=True
        )
        
        auth_service.jobseeker_repo.get_by_email.return_value = MagicMock()

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            auth_service.signup_jobseeker(request)
        
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "이미 등록된 이메일입니다" in exc_info.value.detail

    def test_login_jobseeker_success(self, auth_service):
        # Given
        request = JobseekerLoginRequestDto(email="test@example.com", password="password123")
        
        mock_user = Jobseeker(id=1, email="test@example.com", password="password123", name="Test User")
        auth_service.jobseeker_repo.get_by_email.return_value = mock_user

        # When
        response = auth_service.login_jobseeker(request)

        # Then
        assert response.email == "test@example.com"
        assert response.user_id == 1

    def test_login_jobseeker_fail_wrong_password(self, auth_service):
        # Given
        request = JobseekerLoginRequestDto(email="test@example.com", password="wrongpassword")
        
        mock_user = Jobseeker(id=1, email="test@example.com", password="password123", name="Test User")
        auth_service.jobseeker_repo.get_by_email.return_value = mock_user

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login_jobseeker(request)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signup_company_success(self, auth_service):
        # Given
        request = CompanySignupRequestDto(
            email="company@example.com",
            password="password123",
            name="Test Company",
            company_scale="Startup",
            address="Seoul",
            business_number="123-45-67890",
            policy_agree_bool=True
        )
        
        auth_service.company_repo.get_by_email.return_value = None
        
        mock_company = Company(id=1, email="company@example.com", name="Test Company")
        auth_service.company_repo.create.return_value = mock_company

        # When
        response = auth_service.signup_company(request)

        # Then
        assert response.email == "company@example.com"
        assert response.company_id == 1
        auth_service.company_repo.create.assert_called_once()

    def test_login_company_success(self, auth_service):
        # Given
        request = CompanyLoginRequestDto(email="company@example.com", password="password123")
        
        mock_company = Company(id=1, email="company@example.com", password="password123", name="Test Company")
        auth_service.company_repo.get_by_email.return_value = mock_company

        # When
        response = auth_service.login_company(request)

        # Then
        assert response.email == "company@example.com"
        assert response.company_id == 1
