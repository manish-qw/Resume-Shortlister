import pytest
from models import ResumeData, JobDescription, Skill
from scoring.similarity import score_similarity

def test_similarity_high_analogous_pair():
    resume = ResumeData(
        name="Test",
        skills=[Skill(name="AWS Kinesis")]
    )
    jd = JobDescription(
        title="Data Engineer",
        required_skills=["Apache Kafka"],
        raw_text=""
    )
    result = score_similarity(resume, jd)
    
    assert result.score > 60.0
    assert len(result.analogous_pairs) == 1
    assert result.analogous_pairs[0].resume_skill == "AWS Kinesis"
    assert result.analogous_pairs[0].jd_skill == "Apache Kafka"

def test_similarity_low_match():
    resume = ResumeData(
        name="Test",
        skills=[Skill(name="CSS")]
    )
    jd = JobDescription(
        title="Backend",
        required_skills=["PostgreSQL"],
        raw_text=""
    )
    result = score_similarity(resume, jd)
    
    assert result.score < 50.0
    assert len(result.analogous_pairs) == 0

def test_similarity_empty_skills():
    resume = ResumeData(name="Test", skills=[])
    jd = JobDescription(title="Test", required_skills=["Python"], raw_text="")
    
    result = score_similarity(resume, jd)
    assert result.score == 0.0
