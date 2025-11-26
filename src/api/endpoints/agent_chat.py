from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from services.stt_service.stt_service import stt_service
from agents.chat_agent import get_chat_response

router = APIRouter()

@router.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    """
    음성 파일(Blob)을 받아 STT 모델로 Text로 변환후 LLM을 거쳐 텍스트 응답을 프론트로 반환
    """
    if not file.filename.endswith(".mp3", ".wav", ".webm", ".ogg", ".m4a"):
        raise HTTPException(status_code=400, detail="지원하지 않는 오디오 형식입니다.")
    
    try:
        # 파일 읽기
        audio_bytes = await file.read()

        # STT 변환 (STT 서비스 호출)
        print("음성 변환 시작")
        transcribed_text = stt_service.transcribe(audio_bytes)
        print(f"인식된 텍스트: {transcribed_text}")

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="인식된 텍스트를 찾을 수 없습니다.")
        
        # LLM에 인풋으로 전달
        response = get_chat_response(transcribed_text)
        print(response)

        return JSONResponse(
        content={
            "message": "voice chat processed successfully",
            "response": response
        },
        status_code=200
        )
    
    except Exception as e:
        print(f"음성 채팅 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


