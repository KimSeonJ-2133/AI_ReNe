from sqlalchemy.orm import Session
from models import InterviewSession

class InterviewSessionRepository:
    def __init__(self, db: Session):
        self.db = db
