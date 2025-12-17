from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from core.database import engine, Base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))
from rene_interview import rene_router
from p2p_interview_api import p2p_router
from auth import auth_router
import company_ai_interview_api
from upload_api import upload_router
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ReNe Project API", version="1.0.0")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(p2p_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(company_ai_interview_api.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def init_db():
    print("DB 초기화 스크립트 실행...")
    # Base.metadata.drop_all(bind=engine) # 기존 거 싹 지우고 다시 만들려면 주석 해제
    Base.metadata.create_all(bind=engine) # DB 생성
    print("모든 테이블이 생성되었습니다.")

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../static")

# /static 경로로 들어오는 요청은 static 폴더의 파일을 보여줌. (css, js 등)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 루트 경로('/') 접속 시 index.html 파일을 반환
@app.get("/")
async def read_root():
    # FileResponse(파일경로) 형태로 작성
    return FileResponse(os.path.join(static_dir, "interview_test.html"))

@app.get("/company/ai-interview/report")
async def read_report():
    # FileResponse(파일경로) 형태로 작성
    return FileResponse(os.path.join(static_dir, "company_ai_interview_result.html"))

if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

