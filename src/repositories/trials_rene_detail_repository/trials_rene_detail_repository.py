from sqlalchemy.orm import Session
from models import TrialsReneDetail

class TrialsReneDetailRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, trials_rene: TrialsReneDetail) -> TrialsRene:
        self.db.add(trials_rene)
        self.db.commit()
        self.db.refresh(trials_rene)
        return trials_rene