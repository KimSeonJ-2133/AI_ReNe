import os, sys
import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy.orm import Session
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import text

# [Path 설정] 기존 코드 유지
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.core.database import SessionLocal, engine, Base
from src.models.document import (
    RecruitmentNotice, CompanyIntroduction,Resume, Portfolio, 
)
from src.models.user import (
    Company, JobGroup, Jobseeker
)
from src.models.vector_mapping import (
    JobseekerVectorMapping, CompanyVectorMapping, JobGroupVectorMapping
)
load_dotenv()

db = SessionLocal()

CHROMA_DB_PATH = "./data/chroma_data"
# 디렉토리가 없으면 생성
if not os.path.exists(CHROMA_DB_PATH):
    os.makedirs(CHROMA_DB_PATH)

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# ---------------------------------------------------------
# [Data Definition] 파일 읽기 대신 변수에 직접 할당 (데이터 무결성 보장)
# ---------------------------------------------------------
def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()
            return md_text
    except Exception as e:
        print(f"기업 소개서 파일 읽기 실패: {e}")
        return

# 1. 네이버클라우드 기업 소개 (Markdown)
NAVER_CLOUD_INTRO = read_file("C:\\Users\\user\\potenup\\ReNe\\data\\samples\\naver_cloud_info.txt")

# 2. AI Agent 개발 엔지니어 채용 공고 (Markdown)
NAVER_CLOUD_JD = read_file("C:\\Users\\user\\potenup\\ReNe\\data\\samples\\naver_cloud_jd.txt")
# 3. 이연 이력서 (Markdown)
LEE_YEON_RESUME = read_file("C:\\Users\\user\\potenup\\ReNe\\data\\samples\\yeon_resume.txt")

# 4. 이연 포트폴리오 (Markdown)
LEE_YEON_PORTFOLIO = read_file("C:\\Users\\user\\potenup\\ReNe\\data\\samples\\yeon_portfolio.txt")

# ---------------------------------------------------------
# [Logic] 초기화 함수
# ---------------------------------------------------------


def init_rdb_and_vector_db():
    print("데이터 초기화 시작...")
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("데이터 초기화 완료...")

    try:
        # ==========================================
        # 1. 기업 데이터 생성 (네이버클라우드)
        # ==========================================
        print("기업 데이터 생성: 네이버클라우드")
        
        company = Company(
            name="네이버클라우드",
            email="recruit@navercloud.com", # 가상의 이메일
            password="password123!",
            address="경기도 성남시 분당구 불정로 6 (그린팩토리)",
            business_number="123-45-67890", # 가상의 사업자번호
            company_scale="대기업",
            policy_agree_bool=True
        )
        db.add(company)
        db.flush()

        # 기업 소개서 (Company Introduction)
        company_introduction = CompanyIntroduction(
            company_id=company.id,
            markdown_content=NAVER_CLOUD_INTRO
        )
        db.add(company_introduction)
        
        # 직군 (JobGroup)
        job_group = JobGroup(
            company_id=company.id,
            name="[AI/SW] AI Agent 개발 엔지니어"
        )
        db.add(job_group)
        db.flush()

        # 채용 공고문 (Recruitment Notice)
        recruitment_notice = RecruitmentNotice(
            job_group_id=job_group.id,
            markdown_content=NAVER_CLOUD_JD
        )
        db.add(recruitment_notice)
        print("기업 및 공고 데이터 생성 완료")

        # ==========================================
        # 2. 구직자 데이터 생성 (이연)
        # ==========================================
        print("구직자 데이터 생성: 이연")
        
        jobseeker = Jobseeker(
            name="이연",
            email="dlsdus@naver.com",
            password="password123!",
            phone="010-1234-5678", # 가상의 번호
            birthdate=date(2000, 1, 1), # 가상의 생년월일 (신입 기준)
            gender="FEMALE",
            address="서울특별시 성북구",
            verification_badge="GREEN_CHECK",
            ncs_level=5, # 신입/주니어 레벨로 조정
            rcs_level=4,
            mbti="ESTP", # 임의 설정 (업데이트 가능)
            talent_type="PROVEN_ACE", # 성장 잠재력
            policy_agree_bool=True,
            is_docs_submit="ALL"
        )
        db.add(jobseeker)
        db.flush()

        # 이력서 (Resume)
        resume = Resume(
            jobseeker_id=jobseeker.id,
            brief_self_introduction="데이터 사이언스와 소프트웨어 엔지니어링 역량을 겸비한 '성장하는 육각형' AI 엔지니어",
            
            # [JSON] 학력
            education={
                "school_name": "동덕여자대학교",
                "major": "컴퓨터IT학과",
                "double_major": "데이터사이언스",
                "status": "졸업 예정"
            },
            
            # [JSON] 기술 스택
            skills=[
                "Python", "Java", "Spring Boot", "LangChain", "LangGraph", 
                "RAG", "MySQL", "AWS", "FastAPI", "ChromaDB"
            ],
            
            # [JSON] 경력 (신입이므로 빈 리스트 혹은 인턴 경험 등)
            work_experience=[], 
            
            # [JSON] 프로젝트 요약 (이력서 내 프로젝트 경험 매핑)
            brief_project_introduction=[
                {
                    "title": "지능형 문서 분석 AI Agent",
                    "role": "AI Engineer",
                    "result": "LangGraph 기반 순환형 에이전트 설계 및 RAG 구축"
                },
                {
                    "title": "Farmon (인력 중개 플랫폼)",
                    "role": "Backend Developer",
                    "result": "Spring Boot API 서버 구축 및 AWS 배포"
                },
                {
                    "title": "제주도 관광지 추천 시스템",
                    "role": "ML Engineer",
                    "result": "콘텐츠 기반 필터링 모델 개발"
                }
            ],
            
            # [JSON] 자격증
            certifications=[
                {"name": "빅데이터분석기사", "date": "2024.XX"},
                {"name": "SQLD", "date": "2024.XX"},
                {"name": "캠퍼스 특허 유니버시아드 수상", "date": "2024.XX"}
            ],
            
            # [JSON] 언어
            languages=[
                {"language": "Japanese", "level": "Intermediate", "description": "부전공"}
            ],
            
            # [JSON] 기타 활동
            other_experience=[
                {"activity": "UMC 개발 동아리", "description": "1년 6개월 활동"},
                {"activity": "Hondong 데이터 분석 동아리", "description": "부회장 역임"}
            ],

            ncs_level=5,
            rcs_level=4,
            markdown_content=LEE_YEON_RESUME
        )
        db.add(resume)

        # 포트폴리오 (Portfolio)
        portfolio = Portfolio(
            jobseeker_id=jobseeker.id,
            
            # [JSON] 주요 기술 (포트폴리오 기반)
            main_skills=[
                "LangChain & LangGraph",
                "RAG Pipeline Design",
                "Spring Boot & JPA",
                "AWS (EC2, RDS)",
                "QueryDSL"
            ],
            
            # [JSON] 프로젝트 상세
            project_details=[
                {
                    "title": "지능형 문서 분석 및 질의응답 AI Agent",
                    "role": "Individual Contributor",
                    "skills": ["Python", "LangChain", "LangGraph", "ChromaDB"],
                    "summary": "할루시네이션 최소화를 위한 Advanced RAG 및 자율 에이전트 구현"
                },
                {
                    "title": "Farmon",
                    "role": "Backend Developer",
                    "skills": ["Java", "Spring Boot", "MySQL", "AWS"],
                    "summary": "도농 상생 인력 중개 플랫폼 백엔드 아키텍처 설계 및 구현"
                },
                {
                    "title": "상권 데이터 분석",
                    "role": "Data Analyst",
                    "skills": ["Python", "Selenium", "KoNLPy"],
                    "summary": "가로수길 vs 성수동 상권 비교 분석 및 시각화"
                }
            ],
            
            ncs_level=5,
            rcs_level=4,
            markdown_content=LEE_YEON_PORTFOLIO
        )
        db.add(portfolio)
        db.commit()

        print("구직자 관련 데이터 RDB 저장 완료")

        # ==========================================
        # 3. Vector DB 데이터 삽입
        # ==========================================
        print("Vector DB 데이터 삽입 시작...")

        # 3-1. 기업/공고 Collection
        company_collection_name = "company_recruit_data"
        company_collection = chroma_client.get_or_create_collection(
            name=company_collection_name,
            embedding_function=embedding_function
        )

        company_collection.add(
            ids=[f"company_introduction_{company.id}", f"recruitment_notice_{recruitment_notice.id}"],
            documents=[NAVER_CLOUD_INTRO, NAVER_CLOUD_JD],
            metadatas=[
                {'type': "company_intro", "company_id": company.id},
                {'type': "recruitment_notice", "company_id": company.id, "job_group_id": job_group.id}
            ]
        )
 
        # 3-2. 구직자 Collection
        jobseeker_collection_name = "jobseeker_data"
        jobseeker_collection = chroma_client.get_or_create_collection(
            name=jobseeker_collection_name,
            embedding_function=embedding_function
        )

        jobseeker_collection.add(
            ids=[f"resume_{resume.id}", f"portfolio_{portfolio.id}"],
            documents=[LEE_YEON_RESUME, LEE_YEON_PORTFOLIO],
            metadatas=[
                {'type': "resume", "jobseeker_id": jobseeker.id},
                {'type': "portfolio", "jobseeker_id": jobseeker.id}
            ]
        )

        # ==========================================
        # 4. Mapping Table 업데이트
        # ==========================================
        print("Vector Mapping Table 연결 중...")

        # JobGroup -> VectorDB 매핑
        jg_mapping = JobGroupVectorMapping(
            job_group_id=job_group.id,
            collection_name=company_collection_name,
            collection_type="RECRUITMENT_NOTICE"
        )
        db.add(jg_mapping)

        # Company -> Vector DB 매핑
        c_mapping = CompanyVectorMapping(
            company_id=company.id,
            collection_name=company_collection_name,
            collection_type="COMPANY_INTRODUCTION"
        )
        db.add(c_mapping)

        # Jobseeker -> Vector DB 매핑
        j_mapping = JobseekerVectorMapping(
            jobseeker_id=jobseeker.id,
            collection_name=jobseeker_collection_name,
            collection_type="RESUME_PORTFOLIO"
        )
        db.add(j_mapping)

        db.commit()
        print("모든 데이터 초기화 및 Vector DB 적재 완료!")

    except Exception as e:
        db.rollback()
        print(f"데이터 초기화 중 오류 발생: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()


if __name__ == "__main__":
    init_rdb_and_vector_db()