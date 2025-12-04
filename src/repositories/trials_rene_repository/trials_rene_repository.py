from sqlalchemy.orm import Session

class TrialsReneRepository:
    def __init__(self, db: Session):
        self.db = db