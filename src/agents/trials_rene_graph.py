from typing import Annotated, List, TypedDict, Union, Optional
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# 그래프 상태 정의
class State(TypedDict):
    # 대화 기록 (Langraph가 자동으로 append 처리)
    messages: Annotated[List[BaseMessage], add_messages] # 대화 기록
    current_turn: int # 현재 턴수
    fail_count: int # 연속 실패 횟수(조기 종료용)
    stop_signal: bool # 강제 종료 플래그

    # RAG 검색용 메타데이터
    jobseeker_id: int # 구직자 ID
    company_info: str # ChromaDB에서 가져온 기업 정보
    jobseeker_info: str # ChromaDB에서 가져온 구직자 정보

    # 평가 데이터 (DB 저장용)
    evaluation_history: List[dict]

    # 최종 리포트 데이터 (Analyst 결과)
    final_report: Optional[dict] # 
    interview_summary: Optional[str] # 전체 요약 텍스트    

