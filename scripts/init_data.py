# import os, sys
# import chromadb
# from chromadb.utils import embedding_functions
# from sqlalchemy.orm import Session
# from datetime import date
# from dotenv import load_dotenv
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# from src.core.database import SessionLocal, engine, Base
# from src.models import (
#     Company, JobGroup, RecruitmentNotice, CompanyIntroduction,
#     Jobseeker, Resume, Portfolio, 
#     JobseekerVectorMapping, CompanyVectorMapping, JobGroupVectorMapping
# )
# load_dotenv()

# db = SessionLocal()

# CHROMA_DB_PATH = "../data/chroma_data"
# chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# embedding_function = embedding_functions.OpenAIEmbeddingFunction(
#     model_name="text-embedding-3-small"
# )

# def init_rdb_and_vector_db():
#     print("데이터 초기화 시작...")
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     print("데이터 초기화 완료...")

#     try:
#         print("기업 데이터 생성")
        
#         # 기업 생성(시프트업)
#         company = Company(
#             name="시프트업",
#             email="recruit@shiftup.co.kr",
#             password="12345",
#             address="서울특별시 서초구",
#             business_number="230-81-03325",
#             policy_agree_bool=True
#         )
#         db.add(company)
#         db.flush() # ID 생성위해서 DB에 보냄 (부모 객체에 연결하기 위해)

#         # 기업 소개서 생성(Company Introduction)
#         file_path = "../data/samples/shiftup_company_introduction.txt"
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 company_introduction = f.read()
#         except Exception as e:
#             print(f"기업 소개서 파일 읽기 실패: {e}")
#             return

#         company_introduction = CompanyIntroduction(
#                 company_id=company.id,
#                 markdown_content=company_introduction
#         )

#         db.add(company_introduction)
        
#         # 직군(JobGroup) 생성 
#         job_group = JobGroup(
#             company_id=company.id,
#             name="[Programmer] 테크니컬 아티스트"
#         )

#         db.add(job_group)
#         db.flush() # ID 생성위해서 DB에 보냄

#         # 채용 공고문(Recruitment Notice) 생성
#         file_path = "../data/samples/shiftup_technical_artist.txt"

#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 recruitment_notice = f.read()
#         except Exception as e:
#             print(f"채용 공고문 파일 읽기 실패: {e}")
#             return
        
#         recruitment_notice = RecruitmentNotice(
#             job_group_id=job_group.id,
#             markdown_content=recruitment_notice
#         )

#         db.add(recruitment_notice)

#         print("기업 데이터 생성 완료")

# ## ------------------------------------------------------------

#         print("구직자 데이터 생성 중")
#         jobseeker = Jobseeker(
#             name="김홍범",
#             email="gugu@naver.com",
#             password="12345",
#             phone="010-1234-5678",
#             birthdate=date(1990, 1, 1),
#             gender="MALE",
#             address="서울특별시 서초구",
#             policy_agree_bool=True,
#             verified_grade="NOT_VERIFIED",
#             is_docs_submit="NONE"
#         )

#         db.add(jobseeker)
#         db.flush() # ID 생성위해서 DB에 보냄

#         # 이력서 (Resume)
#         file_path = "../data/samples/hongbeom_resume.txt"

#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 recruitment_notice = f.read()
#         except Exception as e:
#             print(f"이력서 파일 읽기 실패: {e}")
#             return
        
#         resume = Resume(
#             jobseeker_id=jobseeker.id,
#             markdown_content=recruitment_notice
#             brief_self_introduction="Unreal Engine 5 및 Python 툴 개발 역량을 보유한 4년 차 테크니컬 아티스트입니다.",
            
#             # [DB 필드 2] 경력 (JSON): 구조화된 데이터
#             work_experience=[
#                 {
#                     "company_name": "(주)넥스트레벨 게임즈",
#                     "position": "Technical Artist",
#                     "period": "2021.03 ~ 현재",
#                     "description": "UE5 기반 AAA 프로젝트 쉐이더 제작 및 최적화, 파이프라인 툴 개발"
#                 },
#                 {
#                     "company_name": "(주)인디스튜디오",
#                     "position": "Client Developer / TA",
#                     "period": "2020.01 ~ 2021.02",
#                     "description": "모바일 게임 최적화 및 이펙트 제작"
#                 }
#             ],
            
#             # [DB 필드 3] 프로젝트 (JSON): 포트폴리오 요약
#             brief_project_introduction=[
#                 {
#                     "title": "Project N (AAA Open World)",
#                     "role": "Main TA",
#                     "result": "상용화 완료, 메타크리틱 80점 달성"
#                 },
#                 {
#                     "title": "Asset Pipeline Automation Tool",
#                     "role": "Solo Developer",
#                     "result": "사내 표준 툴로 도입"
#                 }
#             ],
            
#             # [DB 필드 4] 학력 (JSON)
#             education={
#                 "school_name": "한국대학교",
#                 "major": "게임공학과",
#                 "status": "졸업",
#                 "period": "2014.03 ~ 2020.02"
#             },
            
#             # [DB 필드 5] 스킬 (JSON)
#             skills=[
#                 "Unreal Engine 5", "Python", "HLSL", "Blueprints", 
#                 "C++", "Shader Optimization", "Substance Designer"
#             ],
            
#             # [DB 필드 6] 자격증 (JSON)
#             certifications=[
#                 {"name": "정보처리기사", "date": "2019.08"},
#                 {"name": "Unity Certified Professional", "date": "2020.05"}
#             ],
            
#             # [DB 필드 7] 어학 (JSON)
#             languages=[
#                 {"language": "English", "level": "Professional Working Proficiency", "score": "OPIc IH"}
#             ],
            
#             # [DB 필드 8] 기타 활동 (JSON)
#             other_experience=[
#                 {"activity": "Unreal Summit 2023 Speaker", "description": "나이트 최적화 사례 발표"}
#             ],

#             # [DB 필드 9] 레벨 (Integer)
#             # 3년 이상 경력 + AAA급 역량 요구 + 우대사항(Houdini, Python) 충족
#             # 1~8 단계 중 '숙련자(Expert)' 수준인 5~6 정도로 설정
#             ncs_level=5, 
#             rcs_level=6,
#         )

#         db.add(resume)







