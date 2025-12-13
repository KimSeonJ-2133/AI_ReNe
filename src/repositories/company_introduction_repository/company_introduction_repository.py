from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models import CompanyIntroduction
import uuid

class CompanyIntroductionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, company_introduction: CompanyIntroduction) -> CompanyIntroduction:
        self.db.add(company_introduction)
        self.db.commit()
        self.db.refresh(company_introduction)
        return company_introduction

    def get_full_text(self, company_id: int):
        """기업 소개서 전체 텍스트 조회"""
        return ""