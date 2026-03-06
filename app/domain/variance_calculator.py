"""
Apeiron CostEstimation Pro – Variance Calculator (Domain)
=========================================================
Variance analysis and classification.
NO imports from persistence, application, or ui layers.
"""

from app.domain.constants import VARIANCE_THRESHOLDS


def calculate_variance(estimated: float, actual: float) -> dict:
    """
    Variance = |Actual – Estimated| / Estimated × 100.
    Classify the result.
    """
    if estimated <= 0:
        return {
            "estimated": estimated,
            "actual": actual,
            "variance_pct": 0.0,
            "classification": "N/A",
            "is_perfect": False,
        }
    variance = round(abs(actual - estimated) / estimated * 100, 2)

    if variance < 5.0:
        classification = "✔ PERFECT ESTIMATE"
        is_perfect = True
    elif variance <= 10.0:
        classification = "Controlled (5–10%)"
        is_perfect = False
    elif variance <= 20.0:
        classification = "Moderate (10–20%)"
        is_perfect = False
    else:
        classification = "High Risk (>20%)"
        is_perfect = False

    return {
        "estimated": estimated,
        "actual": actual,
        "variance_pct": variance,
        "classification": classification,
        "is_perfect": is_perfect,
    }


def classify_variance(variance_pct: float) -> str:
    """Classify a variance percentage into a category string."""
    if variance_pct < 5.0:
        return "PERFECT ESTIMATE"
    elif variance_pct <= 10.0:
        return "Controlled"
    elif variance_pct <= 20.0:
        return "Moderate"
    else:
        return "High Risk"
