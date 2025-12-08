from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models import RecruitmentNotice
import uuid

class RecruitmentNoticeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, recruitment_notice: RecruitmentNotice) -> RecruitmentNotice:
        self.db.add(recruitment_notice)
        self.db.commit()
        self.db.refresh(recruitment_notice)
        return recruitment_notice
