"""Tests for Pydantic models — validation, clamping, and constraints."""

import pytest
from pydantic import ValidationError
from models import ScoreResult, AnalogousPair

def test_score_clamping():
    # Test valid score
    result = ScoreResult(
        scorer_name="test",
        score=85.5,
        evidence=["Some evidence"],
        reasoning="Good score"
    )
    assert result.score == 85.5

    # Test score above 100 clamps to 100
    result_high = ScoreResult(
        scorer_name="test",
        score=150.0,
        evidence=["Some evidence"],
        reasoning="Too high"
    )
    assert result_high.score == 100.0

    # Test score below 0 clamps to 0
    result_low = ScoreResult(
        scorer_name="test",
        score=-10.0,
        evidence=["Some evidence"],
        reasoning="Too low"
    )
    assert result_low.score == 0.0

def test_evidence_not_empty():
    # Should raise validation error when evidence is empty
    with pytest.raises(ValidationError) as exc_info:
        ScoreResult(
            scorer_name="test",
            score=50.0,
            evidence=[],
            reasoning="Valid reasoning"
        )
    assert "At least one evidence item required" in str(exc_info.value)

def test_reasoning_not_empty():
    # Should raise validation error when reasoning is empty string
    with pytest.raises(ValidationError) as exc_info:
        ScoreResult(
            scorer_name="test",
            score=50.0,
            evidence=["Valid evidence"],
            reasoning=""
        )
    assert "Reasoning cannot be empty" in str(exc_info.value)

    # Should raise validation error when reasoning is just whitespace
    with pytest.raises(ValidationError) as exc_info:
        ScoreResult(
            scorer_name="test",
            score=50.0,
            evidence=["Valid evidence"],
            reasoning="   "
        )
    assert "Reasoning cannot be empty" in str(exc_info.value)

def test_analogous_pair():
    pair = AnalogousPair(
        resume_skill="AWS Kinesis",
        jd_skill="Apache Kafka",
        similarity=0.85
    )
    assert pair.similarity == 0.85
