import sys
import os
import uuid
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uvicorn

# [Import] 프로젝트 내부 모듈 연결
# -----
# 실행 위치(src 상위)를 기준으로 경로를 찾을 수 있도록 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 우리가 만든 핵심 서비스 로직 임포트
from src.services.interview_service import process_interview_turn

# [Setup] FastAPI 앱 초기화
# -----
app = FastAPI(title="ReNe AI Interview Service", version="0.1.0")

# [Database]  Mock In-Memory DB (테스트용)
# -----
sessions_db = {}  # session_id -> user_id

# 테스트용 초기 세션 생성 (서버 켤 때마다 리셋됨)
TEST_SESSION_ID = "test_session_123"
TEST_USER_ID = "user_seeker_001"
sessions_db[TEST_SESSION_ID] = TEST_USER_ID

print(f"[Server Init] 테스트용 세션 생성됨: {TEST_SESSION_ID} (User: {TEST_USER_ID})")


# [API] Session (면접 관련)
@app.post("/api/v1/session/growth/chat", tags=["Session"])
async def growth_chat(session_id: str = Form(...), user_audio: UploadFile = File(...)):
    """
    [통합 테스트용] 실제 AI 로직(Evaluator + Persona)이 연결된 기술 면접 API
    - session_id: 'test_session_123'을 넣으세요
    - user_audio: 아무 파일이나 업로드하면 됩니다 (현재 Mock STT가 'Redis...' 인식됨)
    """

    # 세션 검증
    # if session_id not in sessions_db:
    #     raise HTTPException(status_code= 401, detail= "Invalid Session ID")
    user_id = sessions_db.get(session_id, "unknown_user")

    print(f"[API Request] growth_chat 호출됨 (User: {user_id})")

    # 통합 서비스 로직 호출
    # src/services/interview_service.py -> process_interview_turn 실행
    result = await process_interview_turn(
        session_id=session_id, user_id=user_id, audio_file=user_audio
    )

    return {"result_code": 200, "body": result}


# [API] Other Mocks (기타 기능은 껍데기만 유지)
# -----
@app.get("/")
def health_check():
    return {"status": "ok", "message": "ReNe AI Server is Running!"}


@app.post("/api/v1/auth/sign_in", tags=["Auth"])
async def auth_sign_in():
    return {"result_code": 200, "body": {"session_id": TEST_SESSION_ID}}



# 필요한 다른 Mock API가 있다면 아래에 추가

# [Run] 서버 실행 (직접 실행 시)
# -----
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
