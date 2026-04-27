"""
Scoring Orchestrator — fans out to 4 parallel scorers via asyncio.gather().
Computes composite score and applies early-exit optimization.
"""

# TODO: Implement in Phase 8
# - async evaluate(resume, jd, config) -> EvaluationResult
# - asyncio.gather() for parallel scorer execution
# - Early exit: skip LLM scorers if exact_match < floor
# - Composite score calculation with configurable weights
