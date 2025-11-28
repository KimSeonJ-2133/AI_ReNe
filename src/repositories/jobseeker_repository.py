from sqlalchemy.orm import Session
from src.models.user import Jobseeker

class JobseekerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Jobseeker | None:
        return self.db.query(Jobseeker).filter(Jobseeker.email == email).first()

    def create(self, jobseeker: Jobseeker) -> Jobseeker:
        self.db.add(jobseeker)
        self.db.commit()
        self.db.refresh(jobseeker)
        return jobseeker
