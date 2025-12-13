from sqlalchemy.orm import Session

class CompanyAIInterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, company_ai_interview):
        self.db.add(company_ai_interview)
        self.db.commit()
        self.db.refresh(company_ai_interview)
        return company_ai_interview

    