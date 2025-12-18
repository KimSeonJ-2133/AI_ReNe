from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class InterviewMessage(BaseModel):
    role: Literal["interviewer", "interviewee", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class InterviewTurn(BaseModel):
    turn_number: int
    question: str
    answer: Optional[str] = None
    evaluation: Optional[str] = None  # Optional: Immediate feedback or internal thought

class InterviewSessionState(BaseModel):
    session_id: str
    jobseeker_id: int
    company_id: int
    jd_id: int  # RecruitmentNotice ID
    resume_id: int # Resume ID
    status: Literal["ready", "in_progress", "completed", "error"] = "ready"
    current_turn: int = 0
    max_turns: int = 10
    history: List[InterviewMessage] = []
    
class InterviewResponse(BaseModel):
    session_id: str
    message: str
    current_turn: int
    is_finished: bool
