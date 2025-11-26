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
    is_docs_submit = Column(String(20), nullable=True), # NONE, RESUME, PORTFOLIO, ALL
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정 (cascade 삭제 설정)

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

class JobGroup(Base):
    __tablename__ = "job_group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정(cascade 삭제 설정)