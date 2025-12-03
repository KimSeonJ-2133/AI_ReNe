from pydantic import BaseModel, Field

class BeginningReneChatResponseDTO(BaseModel):
    status_code: int = Field(..., description="HTTP Status Code")
    message: str = Field(..., description="Response 메시지 (예: 200 OK)")
    user_text: str = Field(..., description="STT로 변환된 사용자 발화")
    ai_response: str = Field(..., description="LLM의 텍스트 응답")
    audio_base64: str = Field(..., description="TTS로 변환된 오디오 파일 (Base64 인코딩)")

