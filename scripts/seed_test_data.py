import os
import sys
import asyncio
from datetime import date
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.database import SessionLocal, engine, Base
from models.user import Jobseeker, Company, JobGroup
from models.document import Resume, Portfolio, RecruitmentNotice
from services.rag_service import seeker_rag_service, company_rag_service
from core.config import settings

# LangSmith 설정 활성화
if settings.LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    print(f"[Info] LangSmith Tracing Enabled: {settings.LANGSMITH_PROJECT}")

# -----------------------------------------------------------------------------
# 1. 구직자 데이터 (10명)
# -----------------------------------------------------------------------------
SEEKERS_DATA = [
    # --- Senior (1명) ---
    {
        "name": "김수석", "email": "senior@test.com", "career": 12, "level": "최상",
        "intro": "12년차 백엔드 개발자입니다. MSA 전환 및 대용량 트래픽 처리 경험이 풍부합니다.",
        "skills": ["Python", "Go", "Kubernetes", "Kafka", "AWS"],
        "portfolio": """
# 프로젝트: 글로벌 이커머스 플랫폼 MSA 전환
- 역할: Tech Lead / Architect
- 기간: 2021.01 ~ 2023.12
- 내용: 기존 Monolithic 아키텍처를 MSA로 전환하여 배포 주기를 2주에서 1일로 단축.
- 성과: 트래픽 300% 증가에도 안정적인 서비스 운영 달성 (99.99% 가용성).
- 기술: Python(FastAPI), Go, gRPC, Kafka, Kubernetes, AWS EKS
        """
    },
    # --- Mid-Level (4명) ---
    {
        "name": "이중급", "email": "mid1@test.com", "career": 5, "level": "상",
        "intro": "5년차 백엔드 개발자. 코드 품질과 테스트 자동화에 관심이 많습니다.",
        "skills": ["Python", "Django", "Docker", "Redis"],
        "portfolio": """
# 프로젝트: 사내 결제 시스템 고도화
- 역할: 백엔드 개발
- 기간: 2022.03 ~ 2023.08
- 내용: 레거시 결제 모듈 리팩토링 및 비동기 처리 도입.
- 성과: 결제 처리 속도 50% 향상, 테스트 커버리지 80% 달성.
- 기술: Python, Django REST Framework, Celery, Redis
        """
    },
    {
        "name": "박중급", "email": "mid2@test.com", "career": 4, "level": "중",
        "intro": "주어진 기능을 성실히 구현하는 4년차 개발자입니다.",
        "skills": ["Java", "Spring Boot", "MySQL"],
        "portfolio": """
# 프로젝트: 물류 관리 시스템 유지보수
- 역할: 백엔드 개발
- 기간: 2021.06 ~ 2023.06
- 내용: 입출고 관리 API 개발 및 버그 수정.
- 성과: 시스템 안정화 기여.
- 기술: Java, Spring Boot, JPA, MySQL
        """
    },
    {
        "name": "최중급", "email": "mid3@test.com", "career": 3, "level": "중",
        "intro": "협업을 중요시하는 3년차 개발자입니다.",
        "skills": ["Node.js", "Express", "MongoDB"],
        "portfolio": """
# 프로젝트: 사내 메신저 봇 개발
- 역할: 백엔드 개발
- 기간: 2023.01 ~ 2023.06
- 내용: 슬랙 연동 알림 봇 개발.
- 성과: 업무 효율성 증대.
- 기술: Node.js, Express, MongoDB
        """
    },
    {
        "name": "정중급", "email": "mid4@test.com", "career": 3, "level": "하",
        "intro": "3년차 개발자입니다. 시키는 일은 잘 합니다.",
        "skills": ["PHP", "Laravel"],
        "portfolio": """
# 프로젝트: 쇼핑몰 유지보수
- 역할: 유지보수
- 기간: 2021.01 ~ 2023.12
- 내용: 간단한 페이지 수정 및 상품 등록 기능 관리.
- 성과: 운영 지원.
- 기술: PHP, Laravel, MySQL
        """
    },
    # --- Junior (5명) ---
    {
        "name": "강신입", "email": "junior1@test.com", "career": 0, "level": "상",
        "intro": "최신 기술 습득이 빠른 신입 개발자입니다. 오픈소스 기여 경험이 있습니다.",
        "skills": ["Python", "FastAPI", "PyTorch", "LangChain"],
        "portfolio": """
# 프로젝트: AI 기반 법률 상담 챗봇 (개인 프로젝트)
- 역할: 1인 개발
- 기간: 2023.09 ~ 2023.12
- 내용: RAG를 활용한 법률 상담 챗봇 구현.
- 성과: GitHub Star 50개 달성, LangChain PR Merged.
- 기술: Python, FastAPI, LangChain, ChromaDB, OpenAI API
        """
    },
    {
        "name": "조신입", "email": "junior2@test.com", "career": 0, "level": "중",
        "intro": "부트캠프 우수 수료생입니다. 팀 프로젝트 리더 경험이 있습니다.",
        "skills": ["Java", "Spring Boot", "AWS"],
        "portfolio": """
# 프로젝트: 배달 주문 플랫폼 (팀 프로젝트)
- 역할: 팀장, 백엔드 리드
- 기간: 2023.06 ~ 2023.09
- 내용: MSA 기반 배달 플랫폼 프로토타입 개발.
- 성과: 부트캠프 최종 발표 1등.
- 기술: Java, Spring Boot, AWS EC2, RDS
        """
    },
    {
        "name": "윤신입", "email": "junior3@test.com", "career": 0, "level": "중",
        "intro": "기본기가 탄탄한 신입 개발자입니다.",
        "skills": ["Python", "Flask", "SQL"],
        "portfolio": """
# 프로젝트: 도서 관리 시스템 (학부 프로젝트)
- 역할: 백엔드 개발
- 기간: 2023.03 ~ 2023.06
- 내용: 도서 대출/반납 관리 시스템 구현.
- 성과: A+ 학점 취득.
- 기술: Python, Flask, SQLite
        """
    },
    {
        "name": "장신입", "email": "junior4@test.com", "career": 0, "level": "하",
        "intro": "열심히 배우겠습니다.",
        "skills": ["HTML", "CSS", "JavaScript"],
        "portfolio": """
# 프로젝트: 투두 리스트 (클론 코딩)
- 역할: 개발
- 기간: 2023.11 ~ 2023.11
- 내용: 유튜브 강의 보고 따라 만든 투두 리스트.
- 성과: 완성.
- 기술: HTML, CSS, JS
        """
    },
    {
        "name": "임신입", "email": "junior5@test.com", "career": 0, "level": "하",
        "intro": "개발자가 되고 싶습니다.",
        "skills": ["Python"],
        "portfolio": """
# 프로젝트: 계산기 프로그램
- 역할: 개발
- 기간: 2023.10 ~ 2023.10
- 내용: 파이썬으로 만든 콘솔 계산기.
- 성과: 사칙연산 가능.
- 기술: Python
        """
    }
]

# -----------------------------------------------------------------------------
# 2. 기업 데이터 (5개)
# -----------------------------------------------------------------------------
COMPANIES_DATA = [
    {
        "name": "AI Unicorn Corp", "email": "hr@aiunicorn.com", "scale": "유니콘",
        "job_name": "AI Research Engineer",
        "jd": """
# [AI Unicorn] AI Research Engineer 채용

## 주요 업무
- 최신 AI 논문(LLM, Vision) 리서치 및 구현
- 자사 서비스에 적용 가능한 경량화 모델 개발
- 대규모 데이터셋 구축 및 학습 파이프라인 최적화

## 자격 요건
- Python 및 PyTorch/TensorFlow 능숙자
- 최신 논문을 읽고 코드로 구현할 수 있는 분
- 석사 이상 또는 이에 준하는 실무 경력

## 우대 사항
- Top-tier 학회(NeurIPS, ICLR 등) 논문 게재 경험
- 오픈소스 기여 경험
- CUDA 프로그래밍 가능자
        """
    },
    {
        "name": "BigTech Platform", "email": "recruit@bigtech.com", "scale": "대기업",
        "job_name": "Backend Platform Engineer",
        "jd": """
# [BigTech] 백엔드 플랫폼 엔지니어 모집

## 주요 업무
- 대용량 트래픽을 처리하는 공통 플랫폼 개발
- MSA 기반의 서비스 아키텍처 설계 및 운영
- 성능 최적화 및 장애 대응

## 자격 요건
- Java/Kotlin 및 Spring Framework 기반 개발 경험 5년 이상
- 대규모 트래픽 처리 경험
- 분산 시스템에 대한 이해

## 우대 사항
- Kafka, Redis 등 미들웨어 운영 경험
- Kubernetes 환경에서의 개발/운영 경험
        """
    },
    {
        "name": "FinTech Secure", "email": "jobs@fintech.com", "scale": "중견기업",
        "job_name": "Server Developer",
        "jd": """
# [FinTech] 서버 개발자 채용

## 주요 업무
- 금융 거래 시스템 개발 및 운영
- 보안성 높은 API 설계
- 레거시 시스템 개선

## 자격 요건
- Python (Django/FastAPI) 개발 경험 3년 이상
- RDBMS (MySQL, PostgreSQL) 활용 능력
- 금융 도메인에 대한 이해 또는 관심

## 우대 사항
- 금융권 프로젝트 경험
- AWS 클라우드 환경 경험
        """
    },
    {
        "name": "Metaverse Games", "email": "career@metaverse.com", "scale": "스타트업",
        "job_name": "MLOps Engineer",
        "jd": """
# [Metaverse] MLOps 엔지니어 채용

## 주요 업무
- 머신러닝 모델 서빙 파이프라인 구축
- 모델 성능 모니터링 시스템 개발
- 데이터 전처리 자동화

## 자격 요건
- Python, C++ 개발 능력
- Docker, Kubernetes 활용 능력
- CI/CD 파이프라인 구축 경험

## 우대 사항
- Kubeflow, MLflow 사용 경험
- 게임 업계 경험
        """
    },
    {
        "name": "SI Agency", "email": "admin@siagency.com", "scale": "중소기업",
        "job_name": "Junior Backend Developer",
        "jd": """
# [SI Agency] 백엔드 개발자(신입/경력) 모집

## 주요 업무
- 고객사 웹사이트 및 관리자 페이지 개발
- API 연동 및 DB 설계

## 자격 요건
- Python 또는 Java 기초 지식 보유자
- 원활한 커뮤니케이션 능력
- 성실하고 책임감 강하신 분

## 우대 사항
- 정보처리기사 자격증 소지자
- 즉시 출근 가능자
        """
    }
]

def seed_data():
    db = SessionLocal()
    try:
        print("="*50)
        print("Starting Data Seeding...")
        print("="*50)

        # 1. 구직자 생성
        for s_data in SEEKERS_DATA:
            # 중복 체크
            existing = db.query(Jobseeker).filter(Jobseeker.email == s_data["email"]).first()
            if existing:
                print(f"[Skip] Jobseeker already exists: {s_data['name']}")
                jobseeker = existing
            else:
                jobseeker = Jobseeker(
                    name=s_data["name"],
                    email=s_data["email"],
                    password="password123", # Dummy
                    phone="010-0000-0000",
                    birthdate=date(1990, 1, 1),
                    gender="Male",
                    address="Seoul",
                    policy_agree_bool=True,
                    is_docs_submit="PORTFOLIO"
                )
                db.add(jobseeker)
                db.commit()
                db.refresh(jobseeker)
                print(f"[Create] Jobseeker: {s_data['name']} (ID: {jobseeker.id})")

            # 포트폴리오 생성 및 RAG 인덱싱
            # (주의: 실제 서비스 로직에서는 파일 업로드 시점에 수행되지만, 여기서는 직접 DB에 넣고 인덱싱 호출)
            existing_pf = db.query(Portfolio).filter(Portfolio.jobseeker_id == jobseeker.id).first()
            if not existing_pf:
                portfolio = Portfolio(
                    jobseeker_id=jobseeker.id,
                    main_skills=s_data["skills"],
                    project_details=[{"title": "Main Project", "desc": s_data["portfolio"]}], # Simplified
                    markdown_content=f"# 자기소개\n{s_data['intro']}\n\n{s_data['portfolio']}",
                    ncs_level=5, # Dummy
                    rcs_level=5  # Dummy
                )
                db.add(portfolio)
                db.commit()
                db.refresh(portfolio)
                
                # RAG Indexing
                print(f"  -> Indexing Portfolio for {s_data['name']}...")
                seeker_rag_service.index_document(
                    text=portfolio.markdown_content,
                    metadata={
                        "user_id": jobseeker.id,
                        "file_type": "portfolio",
                        "source": "seed_script",
                        "db_record_id": portfolio.id
                    }
                )

        # 2. 기업 생성
        for c_data in COMPANIES_DATA:
            existing_c = db.query(Company).filter(Company.email == c_data["email"]).first()
            if existing_c:
                print(f"[Skip] Company already exists: {c_data['name']}")
                company = existing_c
            else:
                company = Company(
                    name=c_data["name"],
                    email=c_data["email"],
                    password="password123",
                    company_scale=c_data["scale"],
                    address="Seoul",
                    business_number="000-00-00000",
                    policy_agree_bool=True
                )
                db.add(company)
                db.commit()
                db.refresh(company)
                print(f"[Create] Company: {c_data['name']} (ID: {company.id})")

            # JobGroup 생성
            job_group = db.query(JobGroup).filter(JobGroup.company_id == company.id).first()
            if not job_group:
                job_group = JobGroup(company_id=company.id, name=c_data["job_name"])
                db.add(job_group)
                db.commit()
                db.refresh(job_group)

            # JD 생성 및 RAG 인덱싱
            existing_jd = db.query(RecruitmentNotice).filter(RecruitmentNotice.job_group_id == job_group.id).first()
            if not existing_jd:
                jd = RecruitmentNotice(
                    job_group_id=job_group.id,
                    markdown_content=c_data["jd"]
                )
                db.add(jd)
                db.commit()
                db.refresh(jd)
                
                # RAG Indexing
                print(f"  -> Indexing JD for {c_data['name']}...")
                company_rag_service.index_document(
                    text=jd.markdown_content,
                    metadata={
                        "user_id": company.id,
                        "file_type": "company_jd",
                        "source": "seed_script",
                        "db_record_id": jd.id
                    }
                )

        print("="*50)
        print("Data Seeding Completed Successfully!")
        print("="*50)

    except Exception as e:
        print(f"[Error] Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
