from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# from core.config import settings

# llm 초기화
llm = ChatOpenAI(
    model='gpt-4.1-mini',
    temperature=0,
)

# 프론프트 생성
prompt = ChatPromptTemplate.from_template([
    ('system', "당신은 친절하고 유능한 AI 비서입니다. 간결하게 대답하세요."),
    ('useer', '{input}')
])

# 체인 생성 (LCEL)
chain = prompt | llm | StrOutputParser()

async def get_chat_response(input: str) -> str:
    """
    텍스트를 받아 LLM 응답을 반환합니다.
    """
    response = await chain.ainvoke({"input": input})
    return response

