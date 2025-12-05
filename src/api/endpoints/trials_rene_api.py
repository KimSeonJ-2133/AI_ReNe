from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from api.deps import get_db
from src.services.trials_rene_service.trials_rene_service import TrialsReneService
from src.schemas.trials_rene_schemas import trials_rene_request_dto, trials_rene_response_dto

trials_rene_router = APIRouter(prefix="/rene/trials", tags=["Trials Rene"])

@trials_rene_router.post("/voice-chat/process", response_model=trials_rene_response_dto)
def trials_rene_voice_chat(
        request: trials_rene_request_dto,
        db: Session = Depends(get_db)
):
    trials_rene_service = TrialsReneService(db)
    return trials_rene_service.voice_chat(request)