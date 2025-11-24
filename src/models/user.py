import os, sys
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func, Date, Boolean
from sqlalchemy.orm import relationship
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.database import Base

# 구직자 테이블
class Jobseeker(Base):
    __tablename__ = "jobseeker"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    birthdate = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # FEMALE, MALE
    address = Column(String(255), nullable=False)
    verified_grade = Column(String(50), nullable=False)
    policy_agree_bool = Column(Boolean, default=False, nullable=False)
    is_activate = Column(Boolean, default=True, nullable=False)
    is_docs_submit = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 관계 설정 (Cascade 삭제 설정 포함)
    resumes = relationship("Resume", back_populates="jobseeker", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="jobseeker", cascade="all, delete-orphan")
    rene_interviews = relationship("ReneInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    company_ai_interviews = relationship("CompanyAIInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    non_contact_interviews = relationship("NonContactInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    vector_mappings = relationship("JobseekerVectorMapping", back_populates="jobseeker", cascade="all, delete-orphan")