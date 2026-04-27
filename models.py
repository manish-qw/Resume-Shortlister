"""
Pydantic models — single source of truth for all data contracts.

All models used across the parser, scoring engine, classifier,
question generator, and API layer are defined here.
"""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, field_validator


# ── Parser Models (Resume & JD) ──────────────────────────────────────────────

class Skill(BaseModel):
    name: str = Field(description="Name of the skill, e.g., 'Python', 'AWS Kinesis'")
    category: Optional[str] = Field(default=None, description="Category like 'Language', 'Framework', 'Cloud'")
    years: Optional[float] = Field(default=None, description="Years of experience with this skill")

class Experience(BaseModel):
    company: str
    title: str
    duration: str = Field(description="Duration in role, e.g., 'Jan 2020 - Present'")
    description: str = Field(description="Overall description of the role")
    achievements: List[str] = Field(description="Specific achievements or bullet points from this role")

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None

class ResumeData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[Skill] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    links: Dict[str, str] = Field(default_factory=dict, description="e.g., {'github': '...', 'linkedin': '...'}")

class JobDescription(BaseModel):
    title: str
    seniority: str = Field(description="e.g., 'Junior', 'Senior', 'Lead'")
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: str = Field(description="The original raw text of the job description")


# ── Scoring Output Models ──────────────────────────────────────────────────

class AnalogousPair(BaseModel):
    resume_skill: str
    jd_skill: str
    similarity: float = Field(description="Cosine similarity score (0.0 to 1.0)")

class ScoreResult(BaseModel):
    scorer_name: str
    score: float = Field(description="Score out of 100")
    confidence: float = Field(default=1.0, description="Confidence in the score (0.0 to 1.0)")
    evidence: List[str] = Field(description="Evidence supporting the score")
    gaps: List[str] = Field(default_factory=list, description="Missing elements, negative signals, or anti-evidence")
    reasoning: str = Field(description="Human-readable explanation of the score")
    analogous_pairs: Optional[List[AnalogousPair]] = Field(default=None, description="Only populated by Semantic Similarity scorer")

    @field_validator("score")
    def clamp_score(cls, v):
        return max(0.0, min(100.0, float(v)))

    @field_validator("evidence")
    def evidence_not_empty(cls, v):
        if len(v) < 1:
            raise ValueError("At least one evidence item required")
        return v

    @field_validator("reasoning")
    def reasoning_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Reasoning cannot be empty")
        return v


# ── Evaluation Models ──────────────────────────────────────────────────────

class ScoringConfig(BaseModel):
    weight_exact_match: float = 0.30
    weight_similarity: float = 0.25
    weight_achievement: float = 0.25
    weight_ownership: float = 0.20

class EvaluationResult(BaseModel):
    scores: Dict[str, ScoreResult] = Field(description="Results from individual scorers")
    composite: float = Field(description="Final weighted composite score (0-100)")
    tier: Literal["A", "B", "C"] = Field(description="Classification tier")
    questions: List[str] = Field(default_factory=list, description="Tailored interview questions")
    overall_reasoning: str = Field(description="Synthesis of all scorer outputs")


# ── API Models ─────────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    resume: ResumeData
    jd: JobDescription
    config: Optional[ScoringConfig] = None

class EvaluationResponse(BaseModel):
    job_id: str
    status: str
    result: EvaluationResult
