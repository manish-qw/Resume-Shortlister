import os
import json
import logging
from pydantic import BaseModel, Field
import google.generativeai as genai
from models import ResumeData, JobDescription, ScoreResult
from config import settings

logger = logging.getLogger(__name__)

api_key = getattr(settings, 'gemini_api_key', os.environ.get('GEMINI_API_KEY', ''))
genai.configure(api_key=api_key)

class InterviewQuestions(BaseModel):
    questions: list[str] = Field(description="A list of 5 to 8 targeted technical interview questions")

def generate_questions(resume: ResumeData, jd: JobDescription, tier: str, scores: dict[str, ScoreResult]) -> list[str]:
    gaps_text = ""
    for scorer_name, result in scores.items():
        if result.gaps:
            gaps_text += f"[{scorer_name.upper()}] weaknesses: {', '.join(result.gaps)}\n"

    system_instruction = (
        "You are an expert technical interviewer. Based on the candidate's resume, the job description, "
        "their classification tier, and specifically their identified weaknesses, generate 5 to 8 highly targeted "
        "interview questions. The questions should probe their weak areas and verify their strong claims. "
        "Prepend a difficulty label like [Medium] or [Hard] to each question. "
        f"Strictly return a valid JSON object matching this schema:\n"
        f"{json.dumps(InterviewQuestions.model_json_schema())}"
    )

    prompt = (
        f"Candidate Tier: {tier}\n\n"
        f"Job Title: {jd.title}\n"
        f"Required Skills: {', '.join(jd.required_skills)}\n\n"
        f"Candidate Summary: {resume.summary}\n"
        f"Identified Weaknesses / Gaps:\n{gaps_text}"
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
        )
        
        response = model.generate_content(prompt)
        extracted = InterviewQuestions.model_validate_json(response.text.strip())
        return extracted.questions
        
    except Exception as e:
        logger.error(f"Failed to generate questions: {str(e)}")
        return ["Could not generate specific questions at this time due to an API error."]
