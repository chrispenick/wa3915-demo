import os
from typing import Literal
from pydantic import BaseModel, field_validator
from google.adk.agents import LlmAgent

MODEL = os.environ.get("ADK_MODEL", "gemini-2.0-flash")


class CandidateAssessment(BaseModel):
    name: str
    years_experience: int
    key_strengths: list[str]
    recommendation: Literal["advance", "reject", "hold"]

    @field_validator("years_experience")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("years_experience must be non-negative")
        return v


root_agent = LlmAgent(
    name="job_screener",
    model=MODEL,
    instruction=(
        "You are a job application screener. Given a resume or candidate description, "
        "extract the candidate's name, years of experience, top 3 key strengths, "
        "and a hiring recommendation. "
        "Recommendation must be exactly one of: advance, reject, hold."
    ),
    output_schema=CandidateAssessment,
    output_key="assessment",
)
