import os, sys
import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy.orm import Session
from datetime import date
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.core.database import SessionLocal, engine, Base
from src.models import (
    Company, JobGroup, RecruitmentNotice, CompanyIntroduction,
    Jobseeker, Resume, Portfolio, 
    JobseekerVectorMapping, CompanyVectorMapping, JobGroupVectorMapping
)
load_dotenv()

db = SessionLocal()

CHROMA_DB_PATH = "./data/chroma_data"
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

def init_rdb_and_vector_db():
    print("데이터 초기화 시작...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("데이터 초기화 완료...")

    try:
        print("기업 데이터 생성")
        
        # 기업 생성(시프트업)
        company = Company(
            name="시프트업",
            email="recruit@shiftup.co.kr",
            password="12345",
            address="서울특별시 서초구",
            business_number="230-81-03325",
            policy_agree_bool=True
        )
        db.add(company)
        db.flush() # ID 생성위해서 DB에 보냄 (부모 객체에 연결하기 위해)

        # 기업 소개서 생성(Company Introduction)
        file_path = "C:\\Users\\user\\potenup\\ReNe\\scripts\\init_data.py"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                company_introduction_text = f.read()
        except Exception as e:
            print(f"기업 소개서 파일 읽기 실패: {e}")
            return

        company_introduction = CompanyIntroduction(
                company_id=company.id,
                markdown_content=company_introduction_text
        )

        db.add(company_introduction)
        
        # 직군(JobGroup) 생성 
        job_group = JobGroup(
            company_id=company.id,
            name="[Programmer] 테크니컬 아티스트"
        )

        db.add(job_group)
        db.flush() # ID 생성위해서 DB에 보냄

        # 채용 공고문(Recruitment Notice) 생성
        file_path = "C:\\Users\\user\\potenup\\ReNe\\data\\samples\\shiftup_technical_artist.txt"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                recruitment_notice_text = f.read()
        except Exception as e:
            print(f"채용 공고문 파일 읽기 실패: {e}")
            return
        
        recruitment_notice = RecruitmentNotice(
            job_group_id=job_group.id,
            markdown_content=recruitment_notice_text
        )

        db.add(recruitment_notice)

        print("기업 데이터 생성 완료")

## ------------------------------------------------------------

        print("구직자 데이터 생성 중")
        jobseeker = Jobseeker(
            name="김홍범",
            email="gugu@naver.com",
            password="12345",
            phone="010-1234-5678",
            birthdate=date(1990, 1, 1),
            gender="MALE",
            address="서울특별시 서초구",
            policy_agree_bool=True,
            verified_grade="NOT_VERIFIED",
            is_docs_submit="NONE"
        )

        db.add(jobseeker)
        db.flush() # ID 생성위해서 DB에 보냄

        # 이력서 (Resume)
        file_path = "C:\\Users\\user\\potenup\\ReNe\\data\\samples\\hongbeom_resume.txt"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
        except Exception as e:
            print(f"이력서 파일 읽기 실패: {e}")
            return
        
        resume = Resume(
            jobseeker_id=jobseeker.id,
            brief_self_introduction="UE5 AAA 프로젝트 리딩 경험과 Python 툴 개발 역량을 겸비한 5년 차 테크니컬 아티스트입니다.",
            
            # [DB 컬럼] JSON 데이터 (위 텍스트 내용과 1:1 매칭)
            education={"school_name": "한국대학교", "major": "게임공학과", "status": "졸업", "period": "2014.03 ~ 2020.02"},
            
            skills=["Unreal Engine 5", "Python", "HLSL", "C++", "Blueprints", "Optimization", "Houdini"],
            
            work_experience=[
                {
                    "company_name": "(주)넥스트레벨 게임즈",
                    "role": "Lead Technical Artist",
                    "period": "2021.03 ~ 현재",
                    "description": "UE5 AAA 프로젝트 리딩, 렌더링 최적화, Python 툴 개발"
                },
                {
                    "company_name": "(주)인디스튜디오",
                    "role": "Client Programmer & TA",
                    "period": "2020.01 ~ 2021.02",
                    "description": "Unity 모바일 최적화 및 쉐이더 제작"
                }
            ],
            
            brief_project_introduction=[
                {"title": "Project N", "role": "Lead TA", "result": "GPU 비용 25% 절감, 파이프라인 자동화"},
                {"title": "Asset Validator", "role": "Tool Dev", "result": "빌드 안정성 확보"}
            ],
            
            certifications=[
                {"name": "정보처리기사", "date": "2019.08"},
                {"name": "Unity Certified Professional", "date": "2020.05"}
            ],
            
            languages=[
                {"language": "English", "level": "Professional Working Proficiency", "score": "OPIc IH"}
            ],
            
            other_experience=[
                {"activity": "Unreal Summit 2023 Speaker", "description": "Nanite 식생 최적화 발표"}
            ],

            ncs_level=6,
            rcs_level=6,
            markdown_content=resume_text
        )

        db.add(resume)

        file_path = "C:\\Users\\user\\potenup\\ReNe\\data\\samples\\hongbeom_portfolio.txt"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                portfolio_text = f.read()
        except Exception as e:
            print(f"포트폴리오 파일 읽기 실패: {e}")
            return
        
        portfolio = Portfolio(
            jobseeker_id=jobseeker.id,
            
            # [DB 컬럼] 주요 기술 스택 (JSON)
            main_skills=[
                "Unreal Engine 5 (Lumen, Nanite)", 
                "Python Tool Dev (PySide)", 
                "HLSL Shader Programming", 
                "Performance Profiling (RenderDoc)",
                "Houdini Procedural Pipeline"
            ],
            
            # [DB 컬럼] 프로젝트 상세 (JSON) - 텍스트 내용의 구조화 버전
            project_details=[
                {
                    "title": "Project N",
                    "role": "Lead TA",
                    "period": "2021.03 ~ 2024.09",
                    "skills": ["UE5", "Nanite", "Lumen", "Optimization"],
                    "summary": "오픈월드 렌더링 최적화(60fps 방어) 및 마스터 머티리얼 시스템 구축"
                },
                {
                    "title": "Asset Automation Tool",
                    "role": "Tool Developer",
                    "period": "2022.06 ~ 2022.08",
                    "skills": ["Python", "PySide", "Unreal API"],
                    "summary": "에셋 검증(Validator) 및 일괄 처리 자동화 툴 개발, 빌드 안정성 확보"
                },
                {
                    "title": "Procedural Cliff Generator",
                    "role": "Individual Researcher",
                    "period": "2023.01 ~ 2023.03",
                    "skills": ["Houdini", "PCG Framework"],
                    "summary": "절차적 지형 생성 툴 R&D, 레벨 디자인 생산성 300% 향상"
                }
            ],
            
            ncs_level=6,
            rcs_level=6,
            markdown_content=portfolio_text
        )
        db.add(portfolio)
        db.commit() # RDB 저장 완료

        print("구직자 관련 데이터 생성 완료\nVector DB 데이터 삽입 중")

        # --- [Vector DB] 데이터 삽입 ---
        print("floppy_disk Vector DB 데이터 삽입 중")

        # 1. 기업/공고 Collection
        company_collection_name = "company_recruit_data"
        company_collection = chroma_client.get_or_create_collection(
            name=company_collection_name,
            embedding_function=embedding_function
        )

        company_collection.add(
            ids=[f"company_introduction_{company.id}", f"recruitment_notice_{recruitment_notice.id}"],
            documents=[company_introduction_text, recruitment_notice_text],
            metadatas=[
                {'type': "company_intro", "company_id": company.id},
                {'type': "recruitment_notice", "company_id": job_group.company_id, "job_group_id": recruitment_notice.job_group_id}
            ]
        )
 
        # 2. 구직자 Collection
        jobseeker_collection_name = "jobseeker_data"
        jobseeker_collection = chroma_client.get_or_create_collection(
            name=jobseeker_collection_name,
            embedding_function=embedding_function
        )

        jobseeker_collection.add(
            ids=[f"resume_{resume.id}", f"portfolio_{portfolio.id}"],
            documents=[resume_text, portfolio_text],
            metadatas=[
                {'type': "resume", "jobseeker_id": jobseeker.id},
                {'type': "portfolio", "jobseeker_id": jobseeker.id}
            ]

        )

        # --- Mapping Table 업데이트 ---
        print("Vector Mapping Table 연결 중")

        # JobGroup -> VectorDB 매핑 (채용공고용)
        jg_mapping = JobGroupVectorMapping(
            job_group_id=job_group.id,
            collection_name=company_collection_name,
            collection_type="RECRUITMENT_NOTICE"
        )
        db.add(jg_mapping)

        # Company -> Vector DB 매핑 (기업소개서용)
        c_mapping = CompanyVectorMapping(
            company_id=company.id,
            collection_name=company_collection_name,
            collection_type="COMPANY_INTRODUCTION"
        )
        db.add(c_mapping)

        # Jobseeker -> Vector DB 매핑 (이력서용, 포트폴리오용)
        j_mapping = JobseekerVectorMapping(
            jobseeker_id=jobseeker.id,
            collection_name=jobseeker_collection_name,
            collection_type="RESUME_PORTFOLIO"
        )
        db.add(j_mapping)

        db.commit()
        print("모든 데이터 초기화 완료")

    except Exception as e:
        db.rollback()
        print(f"데이터 초기화 중 오류 발생: {e}")
        import traceback
        traceback.format_exc()
    finally:
        db.close()


if __name__ == "__main__":
    init_rdb_and_vector_db()