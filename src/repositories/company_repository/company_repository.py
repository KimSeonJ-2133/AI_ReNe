from sqlalchemy.orm import Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
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
    
    def get_by_id(self, company_id: int) -> Company | None:
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_name(self, company_id: int) -> str:
        company = self.db.query(Company).filter(Company.id == company_id).first()
        return company.name
    
    def get_info_as_markdown(self, company_id: int) -> str:
        """기업 기본 정보를 마크다운 텍스트로 변환하여 반환"""
        company = (
            self.db.query(Company)
            .filter(Company.id == company_id)
            .first()
        )
        
        if not company:
            return "기업 정보를 찾을 수 없습니다."
        
        scale = company.company_scale if company.company_scale else "정보 없음"        

        markdown_text = f"""
## 기업 기본 정보
- **기업명**: {company.name}
- **기업 규모**: {scale}
- **사업자 번호**: {company.business_number}
- **대표 이메일**: {company.email}
- **주소**: {company.address}
"""
        return markdown_text.strip()
