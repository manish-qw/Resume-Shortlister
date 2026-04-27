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

class AchievementExtraction(BaseModel):
    score: float = Field(description="Score from 0 to 100 based on the presence of quantified achievements")
    highlights: list[str] = Field(description="Strong quantified achievements (e.g. 'Increased sales by 20%')")
    weak_signals: list[str] = Field(description="Vague or unquantified claims (e.g. 'Helped improve performance')")
    reasoning: str = Field(description="Explanation of the score")

def score_achievement(resume: ResumeData) -> ScoreResult:
    if not resume.experience and not resume.projects:
        return ScoreResult(
            scorer_name="achievement",
            score=0.0,
            evidence=["No experience or projects found"],
            gaps=["Missing work experience"],
            reasoning="Cannot score achievements without experience or projects."
        )

    text_to_analyze = ""
    for exp in resume.experience:
        text_to_analyze += f"Role: {exp.title} at {exp.company}\nDescription: {exp.description}\nAchievements: {', '.join(exp.achievements)}\n\n"
    
    for proj in resume.projects:
        text_to_analyze += f"Project: {proj.name}\nDescription: {proj.description}\n\n"

    system_instruction = (
        "Analyze the following resume entries for quantified achievements and impact metrics. "
        "STRONG signals: 'Reduced latency by 40%', 'Grew user base from 10K to 100K'. "
        "WEAK signals: 'Helped improve performance', 'Worked on scaling'. "
        f"Strictly return a valid JSON object matching this schema:\n"
        f"{json.dumps(AchievementExtraction.model_json_schema())}"
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
        extracted = AchievementExtraction.model_validate_json(response.text.strip())

        return ScoreResult(
            scorer_name="achievement",
            score=extracted.score,
            evidence=extracted.highlights if extracted.highlights else ["No strong quantified achievements found"],
            gaps=extracted.weak_signals,
            reasoning=extracted.reasoning
        )
        
    except Exception as e:
        logger.error(f"Achievement scoring failed: {str(e)}")
        return ScoreResult(
            scorer_name="achievement",
            score=50.0,
            evidence=["Achievement scoring failed due to API error"],
            gaps=[],
            reasoning="Fallback score due to API error."
        )
