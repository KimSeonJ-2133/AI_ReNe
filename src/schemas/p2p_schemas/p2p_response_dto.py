from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class P2PChunkResponseDto(BaseModel):
    session_id: str
    turn_number: int
    text: str
    status: str = "success"

class P2PReportResponseDto(BaseModel):
    session_id: str
    thinking_process: str
    human_report: str
    update_data: Dict[str, Any]
    raw_response: Optional[str] = None