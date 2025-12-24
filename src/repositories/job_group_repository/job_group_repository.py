from sqlalchemy.orm import Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.models.user import JobGroup

class JobGroupRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_name_by_id(self, job_group_id: int):
        job_group =(
            self.db.query(JobGroup)
            .filter(JobGroup.id == job_group_id)
            .first()
        )
        return job_group.name
    
    
    def get_by_company_id(self, company_id: int) -> int | None:
        job_group = (
            self.db.query(JobGroup)
            .filter(JobGroup.company_id == company_id)
            .order_by(JobGroup.created_at.desc())
            .first()
        )

        return job_group