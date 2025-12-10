from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse, Response
from typing import Optional
import os
import sys
from utils.pdf_utils import convert_pdf_to_image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
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
    # # 임시: 결과 파일 반환
    # base_path = os.path.join("data", "p2p_sessions")
    # file2 = os.path.join(base_path, "면접 결과 요약.png")
            
    # if not os.path.exists(file2):
    #     raise HTTPException(status_code=404, detail="File not found")
    
    # return FileResponse(file2, media_type='image/png', filename="면접 결과 요약.png")

    try:
        # 1. 보고서 생성 (PDF)
        pdf_path = await p2p_service.finalize_p2p_interview()
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Report generation failed (PDF not found)")
            
        # 2. PDF -> Image 변환
        image_path = convert_pdf_to_image(pdf_path)
        
        if not os.path.exists(image_path):
             raise HTTPException(status_code=500, detail="Image conversion failed")
             
        # FileResponse 대신 파일을 읽어서 Response로 반환 (Content-Length 오류 방지)
        with open(image_path, "rb") as f:
            image_content = f.read()
            
        return Response(content=image_content, media_type='image/png')
        
    except Exception as e:
        print(f"Error in audio-chunk2: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @p2p_router.post("/audio-check")
# async def post_audio_check(
#     file: UploadFile = File(...),
#     speaker_role: Optional[str] = Form(None)
# ):
#     """
#     [P2P] 오디오 체크용 엔드포인트
#     """
#     # 임시: 결과 파일 반환

#     print(f"[P2P Audio Check] Received file: {file.filename}, Speaker Role: {speaker_role}")
    
    
#     return {"message": f"Received file '{file.filename}' for speaker role '{speaker_role}'."}

@p2p_router.post("/audio-check", response_model=P2PChunkResponseDto)
async def upload_p2p_session_audio(
    file: UploadFile = File(...),
    speaker_role: str = Form(...)
):
    """
    [P2P] 실시간 오디오 청크 업로드 (PCM)
    - 화자별 버퍼링 및 STT 처리 (단일 세션)
    """
    return await p2p_service.process_p2p_audio_chunk(file, speaker_role)

@p2p_router.get("/report")
async def generate_p2p_report():
    """
    [P2P] 인터뷰 종료 및 보고서 생성 (P2P Auditor Agent)
    - PDF 파일 반환
    """
    pdf_path = await p2p_service.finalize_p2p_interview()
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Report file not found")
        
    filename = os.path.basename(pdf_path)
    return FileResponse(
        path=pdf_path, 
        media_type='application/pdf', 
        filename=filename
    )