from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import Session
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from api.deps import get_db
from services.p2p_service import p2p_service
from schemas.p2p_schemas.p2p_response_dto import P2PChunkResponseDto, P2PReportResponseDto

p2p_router = APIRouter(prefix="/p2p", tags=["P2P Interview"])

@p2p_router.get("/audio-chunk1")
async def get_p2p_audio_chunk1():
    """
    [P2P] 검증 결과 요약 PDF 반환
    """
    # 임시: 결과 파일 반환
    base_path = os.path.join("data", "p2p_sessions")
    file1 = os.path.join(base_path, "검증 결과 요약.pdf")
    
    if not os.path.exists(file1):
        raise HTTPException(status_code=404, detail="File not found")
            
    return FileResponse(file1, media_type='application/pdf', filename="검증 결과 요약.pdf")


@p2p_router.get("/audio-chunk2")
async def get_p2p_audio_chunk2():
    """
    [P2P] 면접 결과 요약 PNG 반환
    """
    # 임시: 결과 파일 반환
    base_path = os.path.join("data", "p2p_sessions")
    file2 = os.path.join(base_path, "면접 결과 요약.png")
            
    if not os.path.exists(file2):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file2, media_type='image/png', filename="면접 결과 요약.png")

@p2p_router.post("/report", response_model=P2PReportResponseDto)
async def generate_p2p_report(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    [P2P] 인터뷰 종료 및 보고서 생성 (P2P Auditor Agent)
    """
    return await p2p_service.finalize_p2p_interview(db, session_id)