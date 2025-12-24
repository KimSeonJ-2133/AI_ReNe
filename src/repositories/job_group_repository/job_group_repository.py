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