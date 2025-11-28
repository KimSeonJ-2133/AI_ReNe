from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from services.meeting_tool_service.meeting_tool_service import process_mentoring, process_team_meeting

app = FastAPI(title="Meeting Log Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용(개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../static")

# /static 경로로 들어오는 요청은 static 폴더의 파일을 보여줍니다. (css, js 등)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 루트 경로('/') 접속 시 index.html 파일을 반환
@app.get("/")
async def read_root():
    # FileResponse(파일경로) 형태로 작성
    return FileResponse(os.path.join(static_dir, "meeting_tool_index.html"))

@app.post("/upload/team-meeting")
async def upload_team_meeting(file: UploadFile = File(...)):
    """
    [팀 회의록] .txt 파일을 업로드하면 요약 후 형식을 정리 해 구글 시트에 저장합니다.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail=".txt 파일만 업로드 가능합니다.")
    
    try:
        content_bytes = await file.read()
        content_text = content_bytes.decode("utf-8")

        # 서비스의 team meetingprocess 로직 호출
        result = process_team_meeting(content_text)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result['message'])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/mentoring")
async def upload_mentoring(file: UploadFile = File(...)):
    """
    [멘토링 회의록] .txt 파일을 업로드하면 요약 후 형식을 정리 해 구글 시트에 저장합니다
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail=".txt 파일만 업로드 가능합니다.")
    
    try:
        content_bytes = await file.read()
        content_text = content_bytes.decode("utf-8")

        # 서비스의 mentoring process 로직 호출
        result = process_mentoring(content_text)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("meeting_tool_app:app", host="0.0.0.0", port=8080, reload=True)

