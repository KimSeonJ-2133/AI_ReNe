from sqlalchemy.orm import Session
import sys, os
from repositories.trials_rene_detail_repository.trials_rene_detail_repository import TrialsReneDetailRepository
from schemas.trials_rene_schemas import trials_rene_response_dto, trials_rene_request_dto

class TrialsReneService:
    def __init__(self, db: Session):
        self.trials_rene_repo = TrialsReneDetailRepository(db)

    def voice_chat(self, request: trials_rene_request_dto) -> trials_rene_response_dto:
        pass
