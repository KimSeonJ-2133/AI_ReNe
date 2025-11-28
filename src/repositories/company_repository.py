from sqlalchemy.orm import Session
from src.models.user import Company

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Company | None:
        return self.db.query(Company).filter(Company.email == email).first()

    def create(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company
