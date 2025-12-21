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
SFA_INTRODUCTION = read_file("C:\\Users\\user\\potenup\\ReNe\\data\\samples\\(주)에스에프에이_기업소개서.txt")

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

        # 기업 소개서 (Company Introduction)
        company_introduction = CompanyIntroduction(
            company_id=2,
            markdown_content=SFA_INTRODUCTION
        )
        db.add(company_introduction)
        db.commit()
        db.refresh(company_introduction)
        print("기업소개서 삽입 완료...")
        

    except Exception as e:
        print(f"기업소개서 삽입 중 오류 발생: {e}")

if __name__ == "__main__":
    init_rdb_and_vector_db()