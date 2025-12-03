from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# 어떤 데이터 타입이든 들어갈 수 있는 변수 T 선언
T = TypeVar("T")

class CommonResponse(BaseModel, Generic[T]):
    message: str = Field("200 OK", description="응답 메시지")
    is_success: bool = Field(True, description="응답 성공 여부")
    data: Optional[T] = Field(None, description="실제 응답 데이터")

