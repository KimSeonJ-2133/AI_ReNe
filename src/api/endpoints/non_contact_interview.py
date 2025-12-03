from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.services.p2p_service import p2p_service
from src.schemas.p2p_schemas.p2p_response_dto import P2PChunkResponseDto, P2PReportResponseDto

router = APIRouter(prefix="/p2p", tags=["P2P Interview"])

@router.post("/audio-chunk/{session_id}", response_model=P2PChunkResponseDto)
async def upload_p2p_audio_chunk(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    [P2P] 오디오 청크 업로드 및 STT 처리
    """
    return await p2p_service.process_p2p_audio_chunk(db, session_id, file)

@router.post("/report/{session_id}", response_model=P2PReportResponseDto)
async def generate_p2p_report(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    [P2P] 인터뷰 종료 및 보고서 생성 (P2P Auditor Agent)
    """
    return await p2p_service.finalize_p2p_interview(db, session_id)