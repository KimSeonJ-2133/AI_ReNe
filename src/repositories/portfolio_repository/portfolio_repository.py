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
