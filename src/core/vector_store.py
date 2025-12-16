import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from core.config import settings

# 벡터 저장소 경로 설정 (프로젝트 루트/data/vector_store)
VECTOR_DB_PATH = os.path.join(os.getcwd(), "data", "vector_store")

def get_vector_store(collection_name: str) -> Chroma:
    """
    ChromaDB 벡터 저장소 인스턴스를 반환합니다.
    
    Args:
        collection_name: 컬렉션 이름 (예: "jobseeker_docs", "company_jds")
        
    Returns:
        Chroma: LangChain 호환 VectorStore 객체
    """
    # 임베딩 모델 초기화 (비용 효율적인 text-embedding-3-small 사용)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY
    )
    
    # ChromaDB 로드 (Persistent)
    # 디렉토리가 없으면 자동으로 생성됨
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    
    return vector_store
