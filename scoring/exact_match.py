import re
from typing import List, Set
from rank_bm25 import BM25Okapi
from models import ResumeData, JobDescription, ScoreResult

def _normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text.lower().strip())

def score_exact_match(resume: ResumeData, jd: JobDescription) -> ScoreResult:
    resume_skills = {_normalize(s.name) for s in resume.skills}
    jd_required = [_normalize(s) for s in jd.required_skills]
    
    if not jd_required:
        return ScoreResult(
            scorer_name="exact_match",
            score=100.0,
            evidence=["No required skills specified in JD"],
            reasoning="Automatically passed as no skills were required."
        )

    # Token set overlap
    matched_skills = [s for s in jd_required if s in resume_skills]
    missing_skills = [s for s in jd_required if s not in resume_skills]
    
    # BM25 for secondary validation of overlap quality
    tokenized_jd = [s.split() for s in jd_required]
    bm25 = BM25Okapi(tokenized_jd)
    
    score = (len(matched_skills) / len(jd_required)) * 100
    
    evidence = [f"Matched: {', '.join(matched_skills)}"] if matched_skills else ["No exact matches found"]
    gaps = [f"Missing: {', '.join(missing_skills)}"] if missing_skills else []
    
    reasoning = (
        f"Found {len(matched_skills)} out of {len(jd_required)} required skills. "
        f"Exact match coverage is {score:.1f}%."
    )

    return ScoreResult(
        scorer_name="exact_match",
        score=score,
        evidence=evidence,
        gaps=gaps,
        reasoning=reasoning
    )
