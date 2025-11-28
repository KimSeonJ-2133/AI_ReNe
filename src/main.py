import sys
import os
import uvicorn

from fastapi import FastAPI, HTTPException, UploadFile, File, Form

# [Import] 프로젝트 내부 모듈 연결
# -----
# 실행 위치(src 상위)를 기준으로 경로를 찾을 수 있도록 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 1. DB 관련 모듈 임포트
from src.core.database import engine, Base

# 모델을 임포트해야 Base.metadata에 테이블 정보가 등록됨.
import src.models.interview

# 서비스 로직 임포트
from src.services.interview_service.interview_service import process_interview_turn

# [Setup] FastAPI 앱 초기화
# -----
app = FastAPI(title="ReNe AI Interview Service (Beta)", version="0.2.0")


def init_db():
    """
    서버 실행 시 DB 테이블을 자동 생성하는 함수
    """
    print("[DB Init] 데이터베이스 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    print("[DB Init] 모든 테이블 생성 완료!")


@app.on_event("startup")
async def startup_event():
    # 앱 시작 시 DB 초기화 실행
    init_db()


# [API] Session (면접 관련)
@app.post("/api/v1/session/growth/chat", tags=["Session"])
async def growth_chat(session_id: str = Form(...), user_audio: UploadFile = File(...)):
    """
    [베타 버전] AI 면접 API
    - 실제 DB의 InterviewSession을 조회하여 대화를 진행합니다.
    - 음성 파일(STT) -> AI(Brain) -> 음성 파일(TTS) 과정을 수행합니다.
    """
    print(f"[API Request] growth_chat 호출됨 (Session: {session_id})")

    # 통합 서비스 로직 호출(DB Session은 Service 내부에서 생성/관리)
    try:
        # process_interview_turn 내부에서 DB 세션을 열고 처리하도록 구현되어야 함
        result = await process_interview_turn(
            session_id=session_id,
            # user_id는 세션 테이블에서 조회하므로 여기선 생략 가능하거나 Service가 처리
            user_id=None,
            audio_file=user_audio,
        )
        return {"result_code": 200, "body": result}
    except Exception as e:
        print(f"[Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# [API] Other Mocks (기타 기능은 껍데기만 유지)
# -----
@app.get("/")
def health_check():
    return {"status": "ok", "message": "ReNe AI Server is Running!"}


@app.post("/api/v1/auth/sign_in", tags=["Auth"])
async def auth_sign_in():
    return {"result_code": 200, "body": {"session_id": "test_session_123"}}


# 필요한 다른 Mock API가 있다면 아래에 추가

# [Run] 서버 실행 (직접 실행 시)
# -----
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
