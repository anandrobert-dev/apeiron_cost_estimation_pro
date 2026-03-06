"""
Apeiron CostEstimation Pro – Input Validators
==============================================
Validation helpers for user input.
"""


def validate_positive(value: float, field_name: str = "value") -> float:
    """Ensure value is positive."""
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")
    return value


def validate_percentage(value: float, field_name: str = "percentage") -> float:
    """Ensure value is a valid percentage (0-100)."""
    if value < 0 or value > 100:
        raise ValueError(f"{field_name} must be between 0 and 100, got {value}")
    return value


def validate_non_empty(text: str, field_name: str = "field") -> str:
    """Ensure text is non-empty after stripping whitespace."""
    text = text.strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty")
    return text
