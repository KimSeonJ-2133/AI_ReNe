import os, sys
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.database import Base

# 구직자 테이블
class Jobseeker(Base):
    __tablename__ = "jobseeker"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)


