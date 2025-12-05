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
