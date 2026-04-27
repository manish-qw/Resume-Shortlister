from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",    
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API Keys ──────────────────────────────────────────────
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude calls",
    )

    # ── Model Configuration ───────────────────────────────────
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model to use for LLM-based scoring",
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model for semantic similarity",
    )

    # ── Scoring Weights (must sum to 1.0) ─────────────────────
    weight_exact_match: float = Field(default=0.30)
    weight_similarity: float = Field(default=0.25)
    weight_achievement: float = Field(default=0.25)
    weight_ownership: float = Field(default=0.20)

    # ── Tier Thresholds ───────────────────────────────────────
    tier_a_threshold: float = Field(
        default=75.0,
        description="Minimum composite score for Tier A (Fast-track)",
    )
    tier_b_threshold: float = Field(
        default=50.0,
        description="Minimum composite score for Tier B (Technical Screen)",
    )

    # ── Scorer Configuration ──────────────────────────────────
    similarity_threshold: float = Field(
        default=0.72,
        description="Cosine similarity threshold for analogous skill pairs",
    )
    exact_match_floor: float = Field(
        default=20.0,
        description="Skip expensive LLM scorers if exact match below this",
    )

    # ── Server ────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)


# Singleton settings instance
settings = Settings()
