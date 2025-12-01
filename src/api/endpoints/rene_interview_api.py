from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os, sys
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from services.stt_service.whisper_large_stt_service import stt_service
from services.tts_service.elevenlabs_tts_service import tts_service
from schemas.beginning_rene_schemas.beginning_rene_response_dto import BeginningReneChatResponseDTO, BeginningReneChatData
from agents.chat_agent import get_chat_response
from dotenv import load_dotenv
load_dotenv()

rene_router = APIRouter()

@rene_router.post("/rene/begin/voice-chat", response_model=BeginningReneChatResponseDTO)
async def voice_chat(file: UploadFile = File(...)):
    """
    음성 파일(Blob)을 받아 STT 모델로 Text로 변환후 LLM을 거쳐 텍스트 응답을 프론트로 반환
    """
    if not file.filename.endswith((".mp3", ".wav", ".webm", ".ogg", ".m4a")):
        raise HTTPException(status_code=400, detail="지원하지 않는 오디오 형식입니다.")
    
    try:
        # 파일 읽기
        audio_bytes = await file.read()

        # STT 변환 (STT 서비스 호출)
        print("음성 변환 시작")
        transcribed_text = stt_service.transcribe(audio_bytes)
        print(f"인식된 텍스트: {transcribed_text}")

        if not transcribed_text:
            raise HTTPException(status_code=500, detail="음성 인식에 실패했습니다.")
        
        # LLM에 인풋으로 전달
        response = await get_chat_response(transcribed_text)
        print(response)

        print("TTS 변환 시작")
        audio_bytes = tts_service.speak(response)

        # Json은 바이너리를 직접 보낼 수 없으므로 문자열로 인코등
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        data = BeginningReneChatData(user_text=transcribed_text, ai_response=response, audio_base64=audio_base64)
        return BeginningReneChatResponseDTO(
            status_code=200,
            message= "200 OK, 음성 채팅에 성공하였습니다.",
            data=data
        )
    
    except Exception as e:
        print(f"음성 채팅 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    


