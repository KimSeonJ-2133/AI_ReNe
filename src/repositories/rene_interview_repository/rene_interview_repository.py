from sqlalchemy.orm import Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.models.interview import ReneInterview

class ReneInterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, rene_interview: ReneInterview) -> ReneInterview:
        self.db.add(rene_interview)
        self.db.commit()
        self.db.refresh(rene_interview)
        return rene_interview