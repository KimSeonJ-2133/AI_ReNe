from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class StartInterviewRequest(BaseModel):
    jobseeker_id: int
    company_id: int
    job_group_id: int

class EndInterviewRequest(BaseModel):
    session_id: str
    
# class InterviewAnswerRequest(BaseModel):
#     session_id: str
#     answer: str   