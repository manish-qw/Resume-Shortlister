import asyncio
from typing import Optional
from models import ResumeData, JobDescription, EvaluationResult, ScoringConfig
from config import settings
from scoring.exact_match import score_exact_match
from scoring.similarity import score_similarity
from scoring.achievement import score_achievement
from scoring.ownership import score_ownership
from classifier import classify
from questions import generate_questions

async def evaluate(resume: ResumeData, jd: JobDescription, config: Optional[ScoringConfig] = None) -> EvaluationResult:
    cfg = config or ScoringConfig()
    
    # 1. Fast Exact Match
    exact_match_result = score_exact_match(resume, jd)
    
    # Early Exit Optimization
    if exact_match_result.score < settings.exact_match_floor:
        overall_reasoning = f"Candidate rejected early: exact match score ({exact_match_result.score:.1f}) is below floor ({settings.exact_match_floor})."
        return EvaluationResult(
            scores={"exact_match": exact_match_result},
            composite=exact_match_result.score,
            tier="C",
            questions=[],
            overall_reasoning=overall_reasoning
        )
    
    # 2. Run remaining scorers concurrently
    similarity_task = asyncio.to_thread(score_similarity, resume, jd)
    achievement_task = asyncio.to_thread(score_achievement, resume)
    ownership_task = asyncio.to_thread(score_ownership, resume)
    
    sim_res, ach_res, own_res = await asyncio.gather(similarity_task, achievement_task, ownership_task)
    
    scores = {
        "exact_match": exact_match_result,
        "similarity": sim_res,
        "achievement": ach_res,
        "ownership": own_res
    }
    
    # 3. Composite Score
    composite = (
        (exact_match_result.score * cfg.weight_exact_match) +
        (sim_res.score * cfg.weight_similarity) +
        (ach_res.score * cfg.weight_achievement) +
        (own_res.score * cfg.weight_ownership)
    )
    
    # 4. Tier & Questions
    tier = classify(composite)
    questions = await asyncio.to_thread(generate_questions, resume, jd, tier, scores)
    
    overall_reasoning = (
        f"Candidate achieved a composite score of {composite:.1f}, placing them in Tier {tier}. "
        f"Strongest area: {max(scores.items(), key=lambda x: x[1].score)[0]}. "
        f"Weakest area: {min(scores.items(), key=lambda x: x[1].score)[0]}."
    )
    
    return EvaluationResult(
        scores=scores,
        composite=round(composite, 2),
        tier=tier,
        questions=questions,
        overall_reasoning=overall_reasoning
    )
