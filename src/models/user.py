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
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    birthdate = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False) # Female, Male
    address = Column(String(255), nullable=False)
    verified_grade = Column(String(50), nullable=False) # NOT_VERIFIED, DOCS_VERIFIED, PERSONAL_VERIFIED,  ALL_VERIFIED
    policy_agree_bool = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_docs_submit = Column(String(20), nullable=True) # NONE, RESUME, PORTFOLIO, ALL
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정 (cascade 삭제 설정)
    resumes = relationship("Resume", back_populates="jobseeker", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="jobseeker", cascade="all, delete-orphan")
    rene_interviews = relationship("ReNeInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    company_ai_interviews = relationship("CompanyAIInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    non_contact_interviews = relationship("NonContactInterview", back_populates="jobseeker", cascade="all, delete-orphan")
    vector_mappings = relationship("JobseekerVectorMapping", back_populates="jobseeker", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    company_scale = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    business_number = Column(String(100), nullable=False) 
    policy_agree_bool = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정 (cascade 삭제 설정)
    job_groups = relationship("JobGroup", back_populates="company", cascade="all, delete-orphan")
    vector_mappings = relationship("CompanyVectorMapping", back_populates="company", cascade="all, delete-orphan")

class JobGroup(Base):
    __tablename__ = "job_group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정(cascade 삭제 설정)
    company = relationship("Company", back_populates="job_groups")
    company_ai_interviews = relationship("CompanyAIInterview", back_populates="job_group", cascade="all, delete-orphan")
    non_concat_interviews = relationship("NonContactInterview", back_populates="job_group", cascade="all, delete-orphann")
    vector_mappings = relationship("JobGroupVectorMapping", back_populates="job_group", cascade="all, delete-orphan")