import os
import sys
import asyncio
import json
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.database import SessionLocal
from models.user import Jobseeker, Company, JobGroup
from models.document import Resume, Portfolio, RecruitmentNotice
from services.interview_service import interview_service
from core.config import settings

# LangSmith 설정 (스크립트 레벨에서 적용)
if settings.LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT

async def run_simulation_batch():
    db = SessionLocal()
    results = []
    
    try:
        print("="*50)
        print("Starting AI2AI Interview Simulation Batch (50 Sessions)")
        print("="*50)

        # 1. 모든 구직자 조회
        seekers = db.query(Jobseeker).all()
        # 2. 모든 기업(채용공고) 조회
        # 편의상 각 기업의 첫 번째 채용공고를 사용
        companies = db.query(Company).all()
        
        total_sessions = len(seekers) * len(companies)
        current_count = 0

        for company in companies:
            # 해당 기업의 채용공고 찾기
            job_group = db.query(JobGroup).filter(JobGroup.company_id == company.id).first()
            if not job_group:
                continue
            notice = db.query(RecruitmentNotice).filter(RecruitmentNotice.job_group_id == job_group.id).first()
            if not notice:
                continue

            for seeker in seekers:
                current_count += 1
                print(f"\n[{current_count}/{total_sessions}] Simulation: {seeker.name} vs {company.name}")
                
                # 해당 구직자의 이력서/포트폴리오 찾기
                # (Seed 데이터에서는 Portfolio만 생성했으므로 Portfolio ID 사용)
                # Resume ID가 필요한 인터페이스라면 Portfolio ID를 대신 넘기거나 수정 필요.
                # 현재 InterviewService는 resume_id를 받아서 seeker_rag_service에 넘김.
                # seeker_rag_service는 db_record_id로 필터링함.
                # Seed 데이터에서 Portfolio를 저장할 때 db_record_id=portfolio.id 로 저장했음.
                portfolio = db.query(Portfolio).filter(Portfolio.jobseeker_id == seeker.id).first()
                if not portfolio:
                    print(f"  -> Skip: No portfolio for {seeker.name}")
                    continue

                # 세션 생성
                session_id = interview_service.create_session(
                    db=db,
                    jobseeker_id=seeker.id,
                    company_id=company.id,
                    jd_id=notice.id,
                    resume_id=portfolio.id 
                )

                # 인터뷰 진행 (5턴 제한)
                # 너무 길어지면 비용/시간 문제 발생하므로 5턴(질문5, 답변5)으로 제한
                MAX_TURNS = 5 
                turns_log = []
                
                try:
                    for turn in range(MAX_TURNS * 2): # 왕복이므로 * 2
                        response = await interview_service.process_next_step(db, session_id)
                        
                        # 로그 저장
                        role = "Company" if turn % 2 == 0 else "Seeker"
                        print(f"  -> [{role}] {response.message[:50]}...") # 내용 일부 출력
                        
                        turns_log.append({
                            "turn": turn + 1,
                            "role": role,
                            "content": response.message
                        })

                        if response.is_finished:
                            break
                            
                except Exception as e:
                    print(f"  -> Error during interview: {e}")
                    turns_log.append({"error": str(e)})

                # 결과 저장
                results.append({
                    "session_id": session_id,
                    "seeker": seeker.name,
                    "company": company.name,
                    "timestamp": datetime.now().isoformat(),
                    "logs": turns_log
                })

        # 결과 파일 저장
        output_dir = os.path.join(os.getcwd(), "data", "logs")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"\n[Success] Simulation completed. Results saved to: {output_file}")

    except Exception as e:
        print(f"[Fatal Error] Simulation batch failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_simulation_batch())
