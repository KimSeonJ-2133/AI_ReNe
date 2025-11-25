import os, sys
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.database import Base

class CompanyVectorMapping(Base):
    __tablename__ = "company_vector_mapping"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    collection_name = Column(String(255), nullable=False)
    collection_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    company = relationship("Company", back_populates="company_vector_mappings")

class JobseekerVectorMapping(Base):
    __tabllename__ = "jobseeker_vector_mapping"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
