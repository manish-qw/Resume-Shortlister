import numpy as np
from sentence_transformers import SentenceTransformer, util
from models import ResumeData, JobDescription, ScoreResult, AnalogousPair
from config import settings

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def score_similarity(resume: ResumeData, jd: JobDescription) -> ScoreResult:
    if not resume.skills or not jd.required_skills:
        return ScoreResult(
            scorer_name="similarity",
            score=0.0,
            evidence=["Insufficient skills for similarity comparison"],
            reasoning="Missing skills in resume or job description."
        )

    model = get_model()
    resume_skills = [s.name for s in resume.skills]
    jd_skills = jd.required_skills

    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    cosine_scores = util.cos_sim(jd_embeddings, resume_embeddings)

    analogous_pairs = []
    total_score = 0.0

    for i, jd_skill in enumerate(jd_skills):
        best_idx = int(np.argmax(cosine_scores[i].cpu().numpy()))
        best_score = float(cosine_scores[i][best_idx])
        
        total_score += best_score

        if best_score >= settings.similarity_threshold:
            analogous_pairs.append(
                AnalogousPair(
                    resume_skill=resume_skills[best_idx],
                    jd_skill=jd_skill,
                    similarity=round(best_score, 3)
                )
            )

    avg_score = (total_score / len(jd_skills)) * 100

    evidence = [f"Found {len(analogous_pairs)} highly similar skill pairs."]
    gaps = [f"Weak matches for {len(jd_skills) - len(analogous_pairs)} required skills."] if len(analogous_pairs) < len(jd_skills) else []

    return ScoreResult(
        scorer_name="similarity",
        score=avg_score,
        evidence=evidence,
        gaps=gaps,
        reasoning=f"Average semantic similarity across required skills is {avg_score:.1f}%.",
        analogous_pairs=analogous_pairs
    )
