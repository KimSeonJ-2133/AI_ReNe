from sqlalchemy.orm import Session
from typing import Optional
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.models.interview import CompanyAIInterviewSession

class CompanyAIInterviewSessionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session: CompanyAIInterviewSession) -> CompanyAIInterviewSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    # 2. 조회 - 단건 (Read by Session ID) -> 가장 중요!
    def get_by_session_id(self, session_id: str) -> Optional[CompanyAIInterviewSession]:
        """
        session_id로 특정 면접 세션 정보를 가져옵니다.
        없으면 None을 반환하므로 Service에서 예외 처리가 필요합니다.
        """
        return (
            self.db.query(CompanyAIInterviewSession)
            .filter(CompanyAIInterviewSession.session_id == session_id)
            .first()
        )

    # # 3. 조회 - 사용자별 목록 (Read List by User ID)
    # def get_all_by_user_id(self, user_id: int) -> List[CompanyAIInterviewSession]:
    #     """
    #     특정 사용자의 모든 면접 기록을 가져옵니다. (마이페이지용)
    #     최신순 정렬 등을 추가하면 좋습니다.
    #     """
    #     return self.db.query(CompanyAIInterviewSession)\
    #         .filter(CompanyAIInterviewSession.user_id == user_id)\
    #         .order_by(CompanyAIInterviewSession.created_at.desc())\
    #         .all()

    # 4. 업데이트 (Update)
    def update(self, session: CompanyAIInterviewSession) -> CompanyAIInterviewSession:
        """
        변경된 세션 객체(turn, history 등)를 DB에 반영합니다.
        SQLAlchemy는 객체가 세션에 attach 되어 있으면 commit만 해도 반영되지만,
        명시적인 메서드를 두는 것이 코드 가독성에 좋습니다.
        """
        self.db.add(session) # 이미 세션에 있다면 생략 가능하지만 안전장치로 둠
        self.db.commit()
        self.db.refresh(session)
        return session