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
    
    def update(self, jobseeker: Jobseeker) -> Jobseeker:
        self.db.add(jobseeker)
        self.db.commit()
        self.db.refresh(jobseeker)
        return jobseeker
    
    def get_by_id(self, jobseeker_id: int) -> Jobseeker | None:
        return self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
    
    # def get_jobseeker_basic_info(self, jobseeker_id: int):
    #     """구직자 기본 정보 반환"""
    #     return self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
    
    def get_name(self, jobseeker_id: int) -> str:
        jobseeker = self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
        return jobseeker.name
    
    def get_info_as_markdown(self, jobseeker_id: int) -> str:
        jobseeker = (
            self.db.query(Jobseeker)
            .filter(Jobseeker.id == jobseeker_id)
            .first()
        )

        if not jobseeker:
            return "구직자 정보를 찾을 수 없습니다."
        
        # None 값일 경우 '정보 없음' 등으로 처리
        mbti = jobseeker.mbti if jobseeker.mbti else "정보 없음"
        ncs = jobseeker.ncs_level if jobseeker.ncs_level else "미측정"
        rcs = jobseeker.rcs_level if jobseeker.rcs_level else "미측정"
        talent = jobseeker.talent_type if jobseeker.talent_type else "미정"

        markdown_text = f"""
## 구직자 기본 프로필
- **이름**: {jobseeker.name}
- **이메일**: {jobseeker.email}
- **연락처**: {jobseeker.phone}
- **생년월일**: {jobseeker.birthdate} ({jobseeker.gender})
- **주소**: {jobseeker.address}
- **인증 뱃지**: {jobseeker.verification_badge}
- **MBTI**: {mbti}

### 역량 및 유형 정보
- **NCS 수준**: {ncs}단계
- **RCS 수준**: {rcs}단계
- **인재 유형**: {talent}
"""
        return markdown_text.strip()

    def update_rcs_and_talent_type(self, jobseeker_id: int, rcs_level: int, talent_type: str) -> None:
        jobseeker = self.db.query(Jobseeker).filter(Jobseeker.id == jobseeker_id).first()
        if jobseeker:
            jobseeker.rcs_level = rcs_level
            jobseeker.talent_type = talent_type
            self.db.commit()