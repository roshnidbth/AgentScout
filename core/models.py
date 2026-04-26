from pydantic import BaseModel, Field, field_validator
from typing import Literal, List

class ProficiencyScore(BaseModel):
    skill: str
    level: int = Field(ge=0, le=5)
    justification: str = Field(min_length=15)
    evidence_quote: str = Field(min_length=8)
    confidence: float = Field(ge=0.6, le=1.0)

class AssessmentState(BaseModel):
    jd_text: str
    resume_text: str
    skills_to_assess: List[str] = []
    current_skill_index: int = 0
    scores: List[ProficiencyScore] = []
    chat_history: List[dict] = []
    status: Literal["in_progress", "complete", "degraded"] = "in_progress"
    learning_plan: dict = {}          