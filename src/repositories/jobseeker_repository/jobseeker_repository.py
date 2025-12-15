from sqlalchemy.orm import Session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.models.user import Jobseeker

class JobseekerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Jobseeker | None:
        """email로 구직자 찾기"""
        return self.db.query(Jobseeker).filter(Jobseeker.email == email).first()

    def create(self, jobseeker: Jobseeker) -> Jobseeker:
        self.db.add(jobseeker)
        self.db.commit()
        self.db.refresh(jobseeker)
        return jobseeker
    
    def get_jobseeker_basic_info(self, jobseeker_id: int):
        """구직자 기본 정보 반환"""
        return self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
    
    def get_name(self, jobseeker_id: int) -> str:
        jobseeker = self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
        return jobseeker.name
    
    def get_info_as_markdown(self, jobseeker_id: int) -> str:
        js = (
            self.db.query(Jobseeker)
            .filter(Jobseeker.id == jobseeker_id)
            .first()
        )

        if not js:
            return "구직자 정보를 찾을 수 없습니다."
        
        # None 값일 경우 '정보 없음' 등으로 처리
        mbti = js.mbti if js.mbti else "정보 없음"
        ncs = js.ncs_level if js.ncs_level else "미측정"
        rcs = js.rcs_level if js.rcs_level else "미측정"
        talent = js.talent_type if js.talent_type else "미정"

        markdown_text = f"""
## 구직자 기본 프로필
- **이름**: {js.name}
- **이메일**: {js.email}
- **연락처**: {js.phone}
- **생년월일**: {js.birthdate} ({js.gender})
- **주소**: {js.address}
- **인증 뱃지**: {js.verification_badge}
- **MBTI**: {mbti}

### 역량 및 유형 정보
- **NCS 수준**: {ncs}단계
- **RCS 수준**: {rcs}단계
- **인재 유형**: {talent}
"""
        return markdown_text.strip()