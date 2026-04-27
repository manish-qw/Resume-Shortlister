import json
import time
import logging
from typing import TypeVar, Type
from pydantic import BaseModel
import google.generativeai as genai
from google.generativeai.types import generation_types

from config import settings
from models import ResumeData, JobDescription
import os

logger = logging.getLogger(__name__)

# Fallback to os.environ if gemini_api_key is not in config.py yet
api_key = getattr(settings, 'gemini_api_key', os.environ.get('GEMINI_API_KEY', ''))
genai.configure(api_key=api_key)

T = TypeVar("T", bound=BaseModel)

def _call_gemini_with_retries(prompt: str, response_model: Type[T], max_retries: int = 2) -> T:

    system_instruction = (
        f"You are an expert recruitment parser. Your task is to extract information "
        f"and strictly return a valid JSON object matching this JSON schema:\n"
        f"{json.dumps(response_model.model_json_schema(), indent=2)}\n\n"
        f"Do not include any explanation or markdown formatting outside the JSON."
    )

    # Use gemini-2.5-flash-lite or pro for structured output
    # We use response_mime_type to enforce JSON output
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=system_instruction,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.0,
        )
    )

    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            raw_json = response.text
            
            return response_model.model_validate_json(raw_json.strip())

        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Failed to parse with Gemini after {max_retries + 1} attempts: {str(e)}")
                raise
            
            wait_time = 2 ** attempt
            logger.warning(f"Gemini API error or validation failure, retrying in {wait_time}s... Error: {str(e)}")
            time.sleep(wait_time)

def parse_resume(raw_text: str) -> ResumeData:

    prompt = (
        f"Please parse the following resume text and extract the structured data.\n\n"
        f"RESUME TEXT:\n"
        f"{raw_text}"
    )
    return _call_gemini_with_retries(prompt, ResumeData)

def parse_job_description(jd_text: str) -> JobDescription:
    prompt = (
        f"Please parse the following job description text and extract the structured data.\n"
        f"Be sure to include the exact raw text in the 'raw_text' field as well.\n\n"
        f"JOB DESCRIPTION TEXT:\n"
        f"{jd_text}"
    )
    
    jd = _call_gemini_with_retries(prompt, JobDescription)
    
    # Ensure raw_text is populated just in case the model missed it
    if not jd.raw_text or jd.raw_text.strip() == "":
        jd.raw_text = jd_text
        
    return jd
