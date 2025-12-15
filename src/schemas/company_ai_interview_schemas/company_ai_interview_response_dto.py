from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class InterviewResponse(BaseModel):
    message: str = Field(..., description="Response 메시지 (예: 200 OK)")
    session_id: str # 세션 ID
    current_turn: int # 현재 면접 턴수
    interview_stage: str # 인터뷰 단계
    ai_message: str  # 면접관(AI)의 질문 또는 안내
    ai_audio_base64: str # 오디오 파일(Base64 인코딩): TTS로 변환된 파일
    status: str   # 'interview', 'done', 'error'