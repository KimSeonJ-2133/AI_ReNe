import uuid
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from core.vector_store import get_vector_store

# 텍스트 분할 설정
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) 기능을 제공하는 서비스 클래스
    문서 인덱싱(저장) 및 검색 기능을 담당합니다.
    """
    
    def __init__(self, collection_name: str):
        self.vector_store = get_vector_store(collection_name)
        
    def index_document(self, text: str, metadata: Dict[str, Any]) -> bool:
        """
        문서를 청크로 분할하여 벡터 DB에 저장합니다.
        
        Args:
            text: 저장할 원본 텍스트
            metadata: 문서 메타데이터 (user_id, file_id, type 등)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 1. 텍스트 분할
            chunks = text_splitter.create_documents([text], metadatas=[metadata])
            
            # 2. 청크별 고유 ID 생성 (중복 방지 및 추적용)
            # LangChain Chroma는 add_documents 시 ids를 지정하지 않으면 자동 생성하지만,
            # 관리를 위해 명시적으로 생성하는 것이 좋을 수 있음. 여기서는 자동 생성에 맡기되,
            # 메타데이터는 모든 청크에 복사됨.
            
            # 3. 벡터 DB에 추가
            self.vector_store.add_documents(chunks)
            print(f"[RAG Service] Indexed {len(chunks)} chunks for file_id: {metadata.get('file_id')}")
            return True
            
        except Exception as e:
            print(f"[RAG Service Error] Indexing failed: {e}")
            return False
            
    def search_similar(self, query: str, filter_metadata: Dict[str, Any], k: int = 5) -> List[Document]:
        """
        유사한 문서 청크를 검색합니다.
        
        Args:
            query: 검색 쿼리
            filter_metadata: 메타데이터 필터 (예: {"user_id": "123"})
            k: 반환할 문서 개수
            
        Returns:
            List[Document]: 검색된 문서 리스트
        """
        try:
            # ChromaDB의 filter 문법 사용
            # 예: collection.query(where={"user_id": "123"})
            
            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter_metadata
            )
            return results
            
        except Exception as e:
            print(f"[RAG Service Error] Search failed: {e}")
            return []

    def delete_document(self, file_id: str):
        """
        특정 파일의 벡터 데이터를 삭제합니다.
        """
        # ChromaDB에서는 where 절을 사용하여 삭제 가능
        # LangChain wrapper에는 delete 메서드가 있음 (ids 필요)
        # 하지만 metadata 기반 삭제는 직접 _collection에 접근하거나 ids를 관리해야 함.
        # 현재 LangChain Chroma 구현상 delete(ids=...) 만 지원하는 경우가 많음.
        # 따라서, 여기서는 구현을 보류하거나, 추후 ids를 별도 관리하는 방식으로 고도화 필요.
        # 임시로: 메타데이터 기반 삭제 시도 (Chroma native)
        try:
            self.vector_store._collection.delete(where={"file_id": file_id})
            print(f"[RAG Service] Deleted documents for file_id: {file_id}")
        except Exception as e:
            print(f"[RAG Service Error] Delete failed: {e}")

# 싱글톤 인스턴스 (필요에 따라 분리 가능)
# 구직자 문서용 (이력서, 포트폴리오)
seeker_rag_service = RAGService("jobseeker_docs")

# 기업 문서용 (JD)
company_rag_service = RAGService("company_jds")
