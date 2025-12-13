from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models import Resume
import uuid

class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_resume_by_jobseeker_id(self, jobseeker_id: int):
        """이력서 조회"""
        return self.db.query(Resume).filter(Resume.jobseeker_id == jobseeker_id).order_by(Resume.created_at.desc()).first()
    
    def get_full_text(self, jobseeker_id: int):
        """이력서 전체 텍스트 조회"""
        return ""