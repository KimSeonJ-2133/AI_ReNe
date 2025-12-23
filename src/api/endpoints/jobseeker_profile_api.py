from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.deps import get_db
from src.models.user import Jobseeker
from src.models.document import Resume, Portfolio
from src.schemas.jobseeker_schemas.jobseeker_profile_dto import JobseekerProfileResponseDto, JobseekerStatsUpdateRequest

profile_router = APIRouter(tags=["Jobseeker Profile"])

@profile_router.get("/jobseeker/profile/{user_id}", response_model=JobseekerProfileResponseDto)
def get_jobseeker_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    구직자 프로필 상세 조회 (Bento Grid용 데이터)
    - 기본 정보, 최신 이력서, 최신 포트폴리오 정보를 통합하여 반환합니다.
    """
    
    # 1. 구직자 기본 정보 조회
    jobseeker = db.query(Jobseeker).filter(Jobseeker.id == user_id).first()
    if not jobseeker:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 2. 최신 이력서 조회
    latest_resume = db.query(Resume)\
        .filter(Resume.jobseeker_id == user_id)\
        .order_by(desc(Resume.created_at))\
        .first()

    # 3. 최신 포트폴리오 조회
    latest_portfolio = db.query(Portfolio)\
        .filter(Portfolio.jobseeker_id == user_id)\
        .order_by(desc(Portfolio.created_at))\
        .first()

    # 4. 데이터 매핑
    
    # 기본값 설정
    education_list = []
    career_list = []
    certifications_list = []
    skills_list = []
    projects_list = []
    links_list = [] # Social Links
    brief_intro = "아직 자기소개가 없습니다."

    # 이력서 데이터 매핑
    if latest_resume:
        brief_intro = latest_resume.brief_self_introduction or brief_intro
        
        # 임시: 이력서 내용에 링크가 있다면 추출하거나, 별도 필드가 없으므로 데모용 더미 데이터 추가 가능
        # 여기서는 데모를 위해 user_id가 1인 경우에만 더미 링크 추가 (실제로는 DB 컬럼 필요)
        if user_id == 1 or user_id == 8: # 8번 유저도 테스트용
            links_list = [
                {"type": "github", "url": "https://github.com/wanted-rene"},
                {"type": "blog", "url": "https://velog.io/@rene"},
                {"type": "linkedin", "url": "https://linkedin.com/in/rene"}
            ]

        # JSON 필드가 리스트인지 확인 후 할당
        if isinstance(latest_resume.education, list):
            education_list = latest_resume.education
        
        if isinstance(latest_resume.work_experience, list):
            career_list = latest_resume.work_experience
            
        if isinstance(latest_resume.certifications, list):
            certifications_list = latest_resume.certifications
            
        # Resume skills는 제외 (Portfolio main_skills만 사용)

    # 포트폴리오 데이터 매핑
    if latest_portfolio:
        if isinstance(latest_portfolio.main_skills, list):
            # 중복 제거하며 병합
            current_skills = set(skills_list)
            for skill in latest_portfolio.main_skills:
                skill_name = None
                if isinstance(skill, str):
                    skill_name = skill
                elif isinstance(skill, dict):
                    if "name" in skill:
                        skill_name = str(skill["name"])
                    elif "skill" in skill:
                        skill_name = str(skill["skill"])
                
                if skill_name and skill_name not in current_skills:
                    skills_list.append(skill_name)
                    current_skills.add(skill_name)
        
        if isinstance(latest_portfolio.project_details, list):
            projects_list = latest_portfolio.project_details

    # DTO 생성
    profile_dto = JobseekerProfileResponseDto(
        user_id=jobseeker.id,
        name=jobseeker.name,
        email=jobseeker.email,
        phone=jobseeker.phone,
        address=jobseeker.address,
        birthdate=str(jobseeker.birthdate),
        gender=jobseeker.gender,
        profile_image_url=None, # TODO: 이미지 업로드 기능 연동
        brief_introduction=brief_intro,
        
        ncs_level=jobseeker.ncs_level or (latest_resume.ncs_level if latest_resume else 1),
        rcs_level=jobseeker.rcs_level or (latest_resume.rcs_level if latest_resume else 1),
        talent_type=jobseeker.talent_type,
        mbti=jobseeker.mbti,
        verification_badge=jobseeker.verification_badge,
        
        main_skills=skills_list,
        education=education_list,
        career=career_list,
        certifications=certifications_list,
        projects=projects_list,
        links=links_list
    )

    return profile_dto


@profile_router.patch("/jobseeker/profile/{user_id}/stats")
def update_jobseeker_stats(
    user_id: int,
    request: JobseekerStatsUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    구직자 NCS, RCS 레벨 및 인재 유형 업데이트
    """
    jobseeker = db.query(Jobseeker).filter(Jobseeker.id == user_id).first()
    if not jobseeker:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    if request.ncs_level is not None:
        jobseeker.ncs_level = request.ncs_level
    if request.rcs_level is not None:
        jobseeker.rcs_level = request.rcs_level
    if request.talent_type is not None:
        jobseeker.talent_type = request.talent_type
        
    db.commit()
    db.refresh(jobseeker)
    
    return {"message": "Stats updated successfully", "ncs_level": jobseeker.ncs_level, "rcs_level": jobseeker.rcs_level, "talent_type": jobseeker.talent_type}
