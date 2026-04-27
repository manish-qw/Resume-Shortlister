import os
import json
import logging
from pydantic import BaseModel, Field
import google.generativeai as genai
from models import ResumeData, ScoreResult
from config import settings

logger = logging.getLogger(__name__)

api_key = getattr(settings, 'gemini_api_key', os.environ.get('GEMINI_API_KEY', ''))
genai.configure(api_key=api_key)

class OwnershipExtraction(BaseModel):
    score: float = Field(description="Score from 0 to 100 based on individual ownership and leadership")
    evidence: list[str] = Field(description="Strong agency signals (e.g., 'Led the design', 'Architected', 'Sole developer')")
    anti_evidence: list[str] = Field(description="Team attribution or weak agency (e.g., 'Assisted', 'Supported', 'Worked on a team')")
    reasoning: str = Field(description="Explanation of the score")

def score_ownership(resume: ResumeData) -> ScoreResult:
    if not resume.experience and not resume.projects:
        return ScoreResult(
            scorer_name="ownership",
            score=0.0,
            evidence=["No experience or projects found"],
            gaps=["Cannot assess ownership without work history"],
            reasoning="Ownership requires experience or project entries to evaluate."
        )

    text_to_analyze = ""
    for exp in resume.experience:
        text_to_analyze += f"Role: {exp.title} at {exp.company}\nDescription: {exp.description}\nAchievements: {', '.join(exp.achievements)}\n\n"
    
    for proj in resume.projects:
        text_to_analyze += f"Project: {proj.name}\nDescription: {proj.description}\n\n"

    system_instruction = (
        "Analyze the following resume entries for signs of individual ownership, leadership, and agency. "
        "Pay special attention to the verbs used and their subjects. "
        "STRONG signals: 'Led', 'Designed', 'Architected', 'Owned', 'Solo delivery'. "
        "WEAK signals (anti-evidence): 'Assisted', 'Supported', 'Participated', 'Contributed to', or statements attributing success purely to 'the team' or 'we'. "
        f"Strictly return a valid JSON object matching this schema:\n"
        f"{json.dumps(OwnershipExtraction.model_json_schema())}"
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            )
        )
        
        response = model.generate_content(text_to_analyze)
        extracted = OwnershipExtraction.model_validate_json(response.text.strip())

        return ScoreResult(
            scorer_name="ownership",
            score=extracted.score,
            evidence=extracted.evidence if extracted.evidence else ["No strong ownership signals found"],
            gaps=extracted.anti_evidence,
            reasoning=extracted.reasoning
        )
        
    except Exception as e:
        logger.error(f"Ownership scoring failed: {str(e)}")
        return ScoreResult(
            scorer_name="ownership",
            score=50.0,
            evidence=["Ownership scoring failed due to API error"],
            gaps=[],
            reasoning="Fallback score due to API error."
        )
