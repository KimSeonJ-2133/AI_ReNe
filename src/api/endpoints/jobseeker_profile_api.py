from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.api.deps import get_db
from src.models.user import Jobseeker
from src.models.document import Resume, Portfolio
from src.schemas.jobseeker_schemas.jobseeker_profile_dto import JobseekerProfileResponseDto

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
    brief_intro = "아직 자기소개가 없습니다."

    # 이력서 데이터 매핑
    if latest_resume:
        brief_intro = latest_resume.brief_self_introduction or brief_intro
        
        # JSON 필드가 리스트인지 확인 후 할당
        if isinstance(latest_resume.education, list):
            education_list = latest_resume.education
        
        if isinstance(latest_resume.work_experience, list):
            career_list = latest_resume.work_experience
            
        if isinstance(latest_resume.certifications, list):
            certifications_list = latest_resume.certifications
            
        # Resume에도 skills가 있을 수 있음
        if isinstance(latest_resume.skills, list):
            for skill in latest_resume.skills:
                if isinstance(skill, str):
                    skills_list.append(skill)
                elif isinstance(skill, dict):
                    # 딕셔너리인 경우 처리 (예: {"name": "Python", "level": "High"})
                    if "name" in skill:
                        skills_list.append(str(skill["name"]))
                    elif "skill" in skill:
                        skills_list.append(str(skill["skill"]))

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
        projects=projects_list
    )

    return profile_dto
