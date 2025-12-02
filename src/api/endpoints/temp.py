from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import random
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from core.database import engine, Base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))
from src.api.endpoints.rene_interview_api import router
import models
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# 서비스 임포트
from src.services.file_upload_service.seeker_file_upload_service import process_file_upload

app = FastAPI(title="ReNe Project Mock API", version="1.0.0")

# ==========================================
# 💾 Stateful Mock DB (메모리 저장소)
# ==========================================
users_db = {}          # email -> User Data
sessions_db = {}       # session_id -> user_id
profiles_db = {}       # user_id -> Profile Data (Seeker)
company_info_db = {}   # user_id -> Company Info
schedules_db = {}      # proposal_id -> Schedule Data
history_db = []        # Completed interviews
scraps_db = {}         # user_id -> List of Company IDs
files_db = {}          # file_id -> File Info
p2p_rooms_db = {}      # schedule_id -> Room Info
analysis_status_db = {} # schedule_id -> Status

# 🟢 테스트용 초기 계정 생성
TEST_SEEKER_EMAIL = "seeker@test.com"
TEST_COMPANY_EMAIL = "company@test.com"
TEST_PW = "1234"

# 1. 구직자 초기 데이터
seeker_id = "user_seeker_001"
users_db[TEST_SEEKER_EMAIL] = {
    "user_id": seeker_id, "email": TEST_SEEKER_EMAIL, "password": TEST_PW, 
    "user_type": "seeker", "user_name": "김구직", "phone": "010-1111-2222"
}
profiles_db[seeker_id] = {
    "summary": {"keywords": ["Creative", "Passion"], "one_line_bio": "성장하는 개발자 김구직입니다."},
    "stats": {"communication": 60, "problem_solving": 50, "technical": 40, "leadership": 30, "adaptability": 70, "ethics": 80},
    "badges": ["badge_newbie"]
}

# 2. 기업 초기 데이터
comp_id = "user_company_001"
users_db[TEST_COMPANY_EMAIL] = {
    "user_id": comp_id, "email": TEST_COMPANY_EMAIL, "password": TEST_PW, 
    "user_type": "company", "user_name": "인사담당자", "company_name": "Samsung Electronics"
}
company_info_db[comp_id] = {
    "name": "Samsung Electronics", "logo": "http://mock-server/samsung_logo.png",
    "reg_num": "123-45-67890", "ongoing_cnt": 2
}

# 🛠 Helper Function
def get_user_id(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid Session")
    return sessions_db[session_id]

# ==========================================
# 1️⃣ Sheet 1. Auth APIs
# ==========================================
class SignUpRequest(BaseModel):
    email: str
    password: str
    user_type: str
    user_name: str
    user_phonenum: str
    user_birth: Optional[int] = None
    user_gender: Optional[str] = None
    user_address: Optional[str] = None
    company_name: Optional[str] = None
    company_reg_num: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

@app.post("/api/v1/auth/check/email", tags=["1. Auth"])
async def auth_email_check(payload: Dict[str, str]):
    is_avail = payload['email'] not in users_db
    return {"result_code": 200, "body": {"is_available": is_avail}}

@app.post("/api/v1/auth/sign_up", tags=["1. Auth"])
async def auth_sign_up(req: SignUpRequest):
    if req.email in users_db:
        return {"result_code": 409, "body": {"error": "Email Duplicated"}}
    
    new_id = str(uuid.uuid4())[:8]
    users_db[req.email] = req.dict()
    users_db[req.email]['user_id'] = new_id
    
    if req.user_type == "seeker":
        profiles_db[new_id] = {
            "summary": {"keywords": [], "one_line_bio": "프로필을 생성해주세요."},
            "stats": {k: 0 for k in ["communication", "problem_solving", "technical", "leadership", "adaptability", "ethics"]},
            "badges": []
        }
    elif req.user_type == "company":
        company_info_db[new_id] = {
            "name": req.company_name, "logo": "", "reg_num": req.company_reg_num, "ongoing_cnt": 0
        }

    return {"result_code": 200, "body": {"user_id": new_id, "user_name": req.user_name}}

@app.post("/api/v1/auth/sign_in", tags=["1. Auth"])
async def auth_sign_in(req: SignInRequest):
    user = users_db.get(req.email)
    if not user or user['password'] != req.password:
        return {"result_code": 400, "body": {"error": "Login Failed"}}
    
    sess_id = f"sess_{uuid.uuid4()}"
    sessions_db[sess_id] = user['user_id']
    return {"result_code": 200, "body": {
        "session_id": sess_id, "user_id": user['user_id'],
        "user_type": user['user_type'], "user_name": user['user_name']
    }}

@app.post("/api/v1/auth/sign_out", tags=["1. Auth"])
async def auth_sign_out(payload: Dict[str, str]):
    if payload.get('session_id') in sessions_db:
        del sessions_db[payload['session_id']]
    return {"result_code": 200, "body": {"is_success": True}}

@app.post("/api/v1/auth/refresh", tags=["1. Auth"])
async def auth_token_refresh(payload: Dict[str, str]):
    # Mock Refresh Logic
    new_sess = f"sess_{uuid.uuid4()}"
    old_sess = payload.get('session_id')
    if old_sess in sessions_db:
        uid = sessions_db[old_sess]
        del sessions_db[old_sess]
        sessions_db[new_sess] = uid
        return {"result_code": 200, "body": {"new_session_id": new_sess}}
    return {"result_code": 401, "body": {"error": "Invalid Token"}}

# ==========================================
# 2️⃣ Sheet 2. User_Seeker APIs
# ==========================================
@app.post("/api/v1/seeker/lobby/load", tags=["2. Seeker"])
async def seeker_lobby_load(payload: Dict[str, str]):
    uid = get_user_id(payload['session_id'])
    prof = profiles_db.get(uid, {})
    return {"result_code": 200, "body": {
        "summary_info": prof.get('summary', {}),
        "stats_graph": prof.get('stats', {}),
        "badges": prof.get('badges', [])
    }}

@app.post("/api/v1/seeker/file/upload", tags=["2. Seeker"])
async def seeker_file_upload(
    session_id: str = Form(...), file_type: str = Form(...), file: UploadFile = File(...)
):
    """
    구직자 파일 업로드 및 LLM 파싱
    
    - session_id: 세션 ID
    - file_type: "resume" 또는 "portfolio"
    - file: 업로드할 파일 (PDF, DOCX, TXT)
    """
    try:
        # 세션에서 user_id 추출
        uid = get_user_id(session_id)
        
        # 실제 파일 처리 (LLM 파싱)
        result = await process_file_upload(
            session_id = session_id,
            file_type = file_type,
            file = file,
            user_id = uid
        )
        
        # Mock DB에도 저장 (호환성 유지)
        files_db[result["file_id"]] = {
            "name": file.filename,
            "owner": session_id,
            "ncs_level": result["ncs_level"],
            "rcs_level": result["rcs_level"],
            "created_at": result["created_at"]
        }
        
        return {"result_code": 200, "body": result}
    
    except HTTPException as he:
        return {"result_code": he.status_code, "body": {"error": he.detail}}
    except Exception as e:
        return {"result_code": 500, "body": {"error": str(e)}}

@app.post("/api/v1/seeker/history/completed", tags=["2. Seeker"])
async def seeker_history_list(payload: Dict[str, Any]):
    uid = get_user_id(payload['session_id'])
    # Filter history for this user
    my_history = [h for h in history_db if h['user_id'] == uid]
    return {"result_code": 200, "body": {"history_list": my_history}}

@app.post("/api/v1/seeker/history/scheduled", tags=["2. Seeker"])
async def seeker_schedule_list(payload: Dict[str, str]):
    uid = get_user_id(payload['session_id'])
    confirmed, pending = [], []
    
    for pid, data in schedules_db.items():
        if data['target_user_id'] == uid:
            item = {"id": pid, "company_name": "Mock Company", "date": data['date'], "msg": data.get('message')}
            if data['status'] == 'confirmed': confirmed.append(item)
            elif data['status'] == 'pending': pending.append({"proposal_id": pid, **item})
            
    return {"result_code": 200, "body": {"confirmed_list": confirmed, "pending_list": pending}}

@app.post("/api/v1/seeker/schedule/action", tags=["2. Seeker"])
async def seeker_schedule_action(payload: Dict[str, str]):
    pid = payload['proposal_id']
    if pid in schedules_db:
        schedules_db[pid]['status'] = 'confirmed' if payload['action'] == 'accept' else 'rejected'
        return {"result_code": 200, "body": {"new_status": schedules_db[pid]['status']}}
    return {"result_code": 400, "body": {"error": "Invalid Proposal ID"}}

@app.post("/api/v1/seeker/report/detail", tags=["2. Seeker"])
async def seeker_report_detail(payload: Dict[str, str]):
    # Mock Report Logic
    return {"result_code": 200, "body": {
        "feedback": {"summary": "훌륭합니다.", "good": ["자신감"], "bad": ["발음"]},
        "audio_url": "http://mock/record.wav"
    }}

@app.post("/api/v1/seeker/scrap/list", tags=["2. Seeker"])
async def seeker_scrap_list(payload: Dict[str, str]):
    uid = get_user_id(payload['session_id'])
    my_scraps = scraps_db.get(uid, [])
    # Mock company details lookup
    result = [{"id": cid, "name": "Scrapped Company"} for cid in my_scraps]
    return {"result_code": 200, "body": {"companies": result}}

@app.post("/api/v1/seeker/scrap/action", tags=["2. Seeker"])
async def seeker_scrap_action(payload: Dict[str, str]):
    uid = get_user_id(payload['session_id'])
    cid = payload['company_id']
    user_scraps = scraps_db.setdefault(uid, [])
    
    if payload['action'] == 'add' and cid not in user_scraps:
        user_scraps.append(cid)
    elif payload['action'] == 'remove' and cid in user_scraps:
        user_scraps.remove(cid)
        
    return {"result_code": 200, "body": {"status": "ok"}}

# ==========================================
# 3️⃣ Sheet 3. User_Company APIs
# ==========================================
@app.post("/api/v1/company/info/load", tags=["3. Company"])
async def company_info_load(payload: Dict[str, str]):
    uid = get_user_id(payload['session_id'])
    info = company_info_db.get(uid, {"name": "Unknown", "logo": "", "ongoing_cnt": 0})
    return {"result_code": 200, "body": {
        "company_name": info['name'], "logo_url": info['logo'], "ongoing_interview_cnt": info['ongoing_cnt']
    }}

@app.post("/api/v1/company/file/upload", tags=["3. Company"])
async def company_file_upload(
    session_id: str = Form(...), file_type: str = Form(...), file: UploadFile = File(...)
):
    fid = f"comp_file_{uuid.uuid4()}"[:8]
    return {"result_code": 200, "body": {"file_id": fid}}

@app.post("/api/v1/company/candidate/list", tags=["3. Company"])
async def company_candidate_list(payload: Dict[str, Any]):
    # 모든 구직자 리턴 (Mock)
    results = []
    for uid, prof in profiles_db.items():
        u = next((u for u in users_db.values() if u['user_id'] == uid), None)
        if u:
            results.append({
                "user_id": uid, "user_name": u['user_name'],
                "keywords": prof['summary']['keywords'],
                "stat_avg": int(sum(prof['stats'].values()) / 6),
                "is_online": True
            })
    return {"result_code": 200, "body": {"candidates": results}}

@app.post("/api/v1/company/candidate/detail", tags=["3. Company"])
async def company_candidate_detail(payload: Dict[str, str]):
    target_uid = payload['target_user_id']
    prof = profiles_db.get(target_uid, {})
    return {"result_code": 200, "body": {
        "summary_info": prof.get('summary'), "stats_graph": prof.get('stats'),
        "badges": prof.get('badges'), "resume_url": "http://mock/resume.pdf"
    }}

@app.post("/api/v1/company/interview/propose", tags=["3. Company"])
async def company_interview_propose(payload: Dict[str, str]):
    prop_id = f"prop_{uuid.uuid4()}"[:8]
    schedules_db[prop_id] = {
        "type": "p2p", "target_user_id": payload['target_user_id'],
        "date": payload['proposed_date'], "message": payload['message'], "status": "pending"
    }
    return {"result_code": 200, "body": {"proposal_id": prop_id}}

@app.post("/api/v1/company/schedule/list", tags=["3. Company"])
async def company_schedule_list(payload: Dict[str, str]):
    # Mock
    return {"result_code": 200, "body": {"confirmed_list": [], "sent_proposals": []}}

@app.post("/api/v1/company/history/completed", tags=["3. Company"])
async def company_history_list(payload: Dict[str, Any]):
    return {"result_code": 200, "body": {"history_list": []}}

@app.post("/api/v1/company/report/detail", tags=["3. Company"])
async def company_report_detail(payload: Dict[str, str]):
    return {"result_code": 200, "body": {"analysis_result": {"score": 90}, "audio_url": "http://mock/rec.wav"}}

# ==========================================
# 4️⃣ Sheet 4. Session Flow APIs
# ==========================================

# 4-1. Beginning (Profile Gen)
@app.post("/api/v1/session/beginning/start", tags=["4. Session"])
async def begin_start(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "interview_id": f"int_beg_{uuid.uuid4()}",
        "npc_text": "반가워요. 당신의 가치관을 알아보기 위한 대화를 시작할게요.",
        "npc_audio_url": "http://mock/audio/beg_intro.wav"
    }}

@app.post("/api/v1/session/beginning/chat", tags=["4. Session"])
async def begin_chat(payload: Dict[str, str]):
    is_fin = "끝" in payload['user_text']
    return {"result_code": 200, "body": {
        "npc_text": f"'{payload['user_text']}'라고 하셨군요. 흥미롭네요.",
        "npc_audio_url": "http://mock/audio/beg_resp.wav",
        "is_finished": is_fin
    }}

@app.post("/api/v1/session/beginning/complete", tags=["4. Session"])
async def begin_complete(payload: Dict[str, str]):
    # Mock Profile Generation Result
    return {"result_code": 200, "body": {"summary_data": {
        "keywords": ["Passion", "Teamwork"], "bio": "열정적인 팀 플레이어입니다."
    }}}

# 4-2. Growth (Practice)
@app.post("/api/v1/session/growth/start", tags=["4. Session"])
async def growth_start(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "interview_id": f"int_gro_{uuid.uuid4()}",
        "npc_text": f"{payload['job_category']} 직무 역량 면접을 시작합니다.",
        "npc_audio_url": "http://mock/audio/gro_intro.wav"
    }}

@app.post("/api/v1/session/growth/chat", tags=["4. Session"])
async def growth_chat(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "npc_text": "구체적인 경험이 있나요?", "npc_audio_url": "http://mock/audio/gro_q.wav", "feedback_hint": "STAR 기법으로 답변해보세요."
    }}

@app.post("/api/v1/session/growth/complete", tags=["4. Session"])
async def growth_complete(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "stat_changes": {"technical": 5, "communication": 3}, "new_badges": ["lvl1_dev"]
    }}

# 4-3. Trials (Company Practice)
@app.post("/api/v1/session/trial/start", tags=["4. Session"])
async def trial_start(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "interview_id": f"int_tri_{uuid.uuid4()}",
        "npc_text": "삼성전자 모의 면접입니다. 압박 질문에 대비하세요.",
        "npc_audio_url": "http://mock/audio/tri_intro.wav"
    }}

@app.post("/api/v1/session/trial/chat", tags=["4. Session"])
async def trial_chat(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "npc_text": "우리 회사의 인재상에 대해 아시나요?", "npc_audio_url": "http://mock/audio/tri_q.wav"
    }}

@app.post("/api/v1/session/trial/complete", tags=["4. Session"])
async def trial_complete(payload: Dict[str, str]):
    return {"result_code": 200, "body": {"report_id": f"rep_{uuid.uuid4()}"}}

# 4-4. Real (Company Application)
@app.post("/api/v1/session/real/start", tags=["4. Session"])
async def real_start(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "interview_id": f"int_real_{uuid.uuid4()}",
        "npc_text": "실전 면접입니다. 기록이 저장됩니다.", "npc_audio_url": "http://mock/audio/real_intro.wav"
    }}

@app.post("/api/v1/session/real/chat", tags=["4. Session"])
async def real_chat(payload: Dict[str, str]):
    return {"result_code": 200, "body": {
        "npc_text": "마지막으로 하고 싶은 말이 있나요?", "npc_audio_url": "http://mock/audio/real_q.wav"
    }}

@app.post("/api/v1/session/real/submit", tags=["4. Session"])
async def real_submit(payload: Dict[str, str]):
    return {"result_code": 200, "body": {"submission_date": "2025-11-25"}}

# 4-5. P2P Session
@app.post("/api/v1/session/p2p/create", tags=["4. Session"])
async def p2p_room_create(payload: Dict[str, str]):
    # Mock Dedic Server Allocation
    sid = payload['schedule_id']
    room_info = {"room_ip": "127.0.0.1", "room_port": 7777, "room_token": f"tok_{uuid.uuid4()}"}
    p2p_rooms_db[sid] = room_info
    return {"result_code": 200, "body": room_info}

@app.post("/api/v1/session/p2p/join", tags=["4. Session"])
async def p2p_room_join(payload: Dict[str, str]):
    sid = payload['schedule_id']
    if sid in p2p_rooms_db:
        return {"result_code": 200, "body": p2p_rooms_db[sid]}
    return {"result_code": 404, "body": {"error": "Room Not Created"}}

@app.post("/api/v1/session/p2p/status", tags=["4. Session"])
async def p2p_status_update(payload: Dict[str, str]):
    # e.g., Started or Finished logging
    return {"result_code": 200, "body": {"status": "updated"}}

# ==========================================
# 5️⃣ Sheet 5. Analysis APIs
# ==========================================
@app.post("/api/v1/analysis/p2p/upload", tags=["5. Analysis"])
async def p2p_upload_record(
    session_id: str = Form(...), schedule_id: str = Form(...),
    role: str = Form(...), file: UploadFile = File(...)
):
    # Mock Logic: If both uploaded, start processing
    analysis_status_db[schedule_id] = "processing"
    return {"result_code": 200, "body": {"upload_status": "success", "waiting_for_partner": False}}

@app.post("/api/v1/analysis/p2p/status", tags=["5. Analysis"])
async def p2p_analysis_status(payload: Dict[str, str]):
    sid = payload['schedule_id']
    status = analysis_status_db.get(sid, "uploading")
    
    # Mock Progress
    pct = 50 if status == "processing" else 100 if status == "completed" else 0
    if status == "processing":
        # Randomly complete it for testing
        if random.random() > 0.8: 
            analysis_status_db[sid] = "completed"
            
    return {"result_code": 200, "body": {"status": status, "progress_pct": pct}}

@app.post("/api/v1/analysis/p2p/retry", tags=["5. Analysis"])
async def p2p_analysis_retry(payload: Dict[str, str]):
    analysis_status_db[payload['schedule_id']] = "processing"
    return {"result_code": 200, "body": {"status": "processing"}}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

