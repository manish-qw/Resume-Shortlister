from typing import Literal
from config import settings

def classify(composite: float) -> Literal["A", "B", "C"]:
    """Classify candidate tier based on composite score."""
    if composite >= settings.tier_a_threshold:
        return "A"
    elif composite >= settings.tier_b_threshold:
        return "B"
    else:
        return "C"
