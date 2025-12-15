from sqlalchemy.orm import Session
from models import CompanyAIInterview
from datetime import datetime

class CompanyAIInterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, interview_data: dict):
        """
        딕셔너리 데이터를 받아서 CompanyAIInterview 엔티티를 생성하고 저장
        """
        try:
            # DTO 변환이나 데이터 매핑 로직
            interview = CompanyAIInterview(
                jobseeker_id=interview_data["jobseeker_id"],
                job_group_id=interview_data["job_group_id"],
                session_id=interview_data["session_id"],
                report=interview_data["report"],
                summary=interview_data["summary"],
                total_score=interview_data["total_score"],
                skills_evaluation=interview_data["skills_evaluation"], # JSON/List 그대로 들어감
                ai_result=interview_data["ai_result"],
                best_answer=interview_data["best_answer"],
                worst_answer=interview_data["worst_answer"],
                total_advice=interview_data["total_advice"],
                end_time=datetime.now()
            )
            self.db.add(interview)
            self.db.commit()
            self.db.refresh(interview)
            return interview
        except Exception as e:
            self.db.rollback()
            raise e

