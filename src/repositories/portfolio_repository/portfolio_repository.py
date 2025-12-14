from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models import Portfolio
import uuid

class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, portfolio: Portfolio) -> Portfolio:
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_full_text(self, jobseeker_id: int):
        """포트폴리오 전체 텍스트 조회"""
        portfolio = (
            self.db.query(Portfolio)
            .filter(Portfolio.jobseeker_id == jobseeker_id)
            .order_by(Portfolio.created_at.desc())
            .first()
        )
        return portfolio.markdown_content if portfolio else ""