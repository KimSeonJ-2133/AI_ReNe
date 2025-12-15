from sqlalchemy.orm import Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.models.interview import TrialsReneDetail

class TrialsReneDetailRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, trials_rene: TrialsReneDetail) -> TrialsReneDetail:
        self.db.add(trials_rene)
        self.db.commit()
        self.db.refresh(trials_rene)
        return trials_rene