from fastapi import APIRouter, UploadFile, File, HTTPException
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from services.stt_service.whisper_large_stt_service import stt_service
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

@router.post("/non-contact/voice-chat-save")
async def voice_chat(file: UploadFile = File(...)):
    return None

@router.post("/non-contact/report")
async def report(user_id: int):
    return None

