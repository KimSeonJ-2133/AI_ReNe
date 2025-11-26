import os, sys
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, func, Text, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.database import Base

# 1. 르네 인터뷰 (SuperType)
class ReNeInterview(Base):
    __tablename__ = "rene_interview"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jobseeker_id = Column(Integer, ForeignKey("jobseeker.id", ondelete="CASCADE"), nullable=False) # 외래키
    interview_type = Column(String(50), nullable=False)
    full_transcript = Column(LONGTEXT, nullable=False)
    summary = Column(LONGTEXT, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    jobseeker = relationship("Jobseeker", back_populates="rene_interviews")

    # 1:1 매핑 관계 설정 (uselist=False)
    beginning_rene_detail = relationship("BeginningReneDetail", back_populates="rene_interview", uselist=False, cascade="all, delete-orphan")
    growth_rene_detail = relationship("GrowthReneDetail", back_populates="rene_interview", uselist=False, cascade="all, delete-orphan")
    trials_rene_detail = relationship("TrialsReneDetail", back_populates="rene_interview", uselist=False, cascade="all, delete-orphan")


# 2. 시작의 르네 인터뷰 (SubType)
class BeginningReneDetail(Base):
    __tablename__ = "beginning_rene_detail"

    # 1:1 식별관계
    id = Column(Integer, ForeignKey("rene_interview.id", ondelete="CASCADE"), primary_key=True)
    occupational_skills = Column(JSON, nullable=False)
    mbti = Column(String(10), nullable=False)
    recommended_jobs = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    rene_interview = relationship("ReneInterview", back_populates="beginning_rene_detail")


# 3. 성장의 르네 인터뷰 (SubType)
class GrowthReneDetail(Base):
    __tablename__ = "growth_rene_detail"

    id = Column(Integer, ForeignKey("rene_interview.id", ondelete="CASCADE"), primary_key=True)
    project_details = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    rene_interview = relationship("ReneInterview", back_populates="growth_rene_detail")


# 4. 시련의 르네 인터뷰 (SubType)
class TrialsReneDetail(Base):
    __tablename__ = "trials_rene_detail"

    id = Column(Integer, ForeignKey("rene_interview.id", ondelete="CASCADE"), primary_key=True)
    total_score = Column(Float, nullable=False)
    total_evaluation = Column(JSON, nullable=False)
    ai_result = Column(String(20), nullable=False) # PASS, FAIL, HOLD
    best_answer = Column(Text, nullable=False)
    worst_answer = Column(Text, nullable=False)
    total_advice = Column(LONGTEXT, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    rene_interview = relationship("ReneInterview", back_populates="trials_rene_detail")


# 5. 기업 AI 면접
class CompanyAIInterview(Base):
    __tablename__ = "company_ai_interview"

    id = Column(Integer, primary_key=True, index=True)
    jobseeker_id = Column(Integer, ForeignKey("jobseeker.id", ondelete="CASCADE"), nullable=False)
    job_group_id = Column(Integer, ForeignKey("job_group.id", ondelete="CASCADE"), nullable=False)
    full_transcript = Column(LONGTEXT, nullable=False)
    summary = Column(Text, nullable=False)
    total_score = Column(Float, nullable=False)
    total_evaluation = Column(JSON, nullable=False)
    ai_result = Column(String(20), nullable=False)
    best_answer = Column(Text, nullable=False)
    worst_answer = Column(Text, nullable=False)
    total_advice = Column(Text, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    jobseeker = relationship("Jobseeker", back_populates="company_ai_interviews")
    job_group = relationship("JobGroup", back_populates="company_ai_interviews")


# 6. 비대면 화상 면접
class NonContactInterview(Base):
    __tablename__ = "non_contact_interview"

    id = Column(Integer, primary_key=True, index=True)
    jobseeker_id = Column(Integer, ForeignKey("jobseeker.id", ondelete="CASCADE"), nullable=False)
    job_group_id = Column(Integer, ForeignKey("job_group.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    is_end = Column(Boolean, default=False, nullable=False)
    full_transcript = Column(LONGTEXT, nullable=True)
    summary = Column(Text, nullable=True)
    total_score = Column(Float, nullable=True)
    total_evaluation = Column(JSON, nullable=True)
    best_answer = Column(Text, nullable=True)
    worst_answer = Column(Text, nullable=True)
    total_advice = Column(Text, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    jobseeker = relationship("Jobseeker", back_populates="non_contact_interviews")
    job_group = relationship("JobGroup", back_populates="non_contact_interviews")