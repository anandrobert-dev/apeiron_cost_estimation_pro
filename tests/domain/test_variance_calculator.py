"""
Tests for app.domain.variance_calculator – Pure domain logic.
No DB fixtures needed.
"""

from app.domain.variance_calculator import calculate_variance, classify_variance


class TestCalculateVariance:
    def test_perfect_estimate(self):
        result = calculate_variance(100000, 103000)
        assert result["variance_pct"] == 3.0
        assert result["is_perfect"] is True
        assert "PERFECT" in result["classification"]

    def test_controlled(self):
        result = calculate_variance(100000, 108000)
        assert result["variance_pct"] == 8.0
        assert "Controlled" in result["classification"]

    def test_moderate(self):
        result = calculate_variance(100000, 115000)
        assert "Moderate" in result["classification"]

    def test_high_risk(self):
        result = calculate_variance(100000, 125000)
        assert "High Risk" in result["classification"]

    def test_zero_estimated(self):
        result = calculate_variance(0, 100)
        assert result["classification"] == "N/A"

    def test_under_estimate(self):
        result = calculate_variance(100000, 80000)
        assert result["variance_pct"] == 20.0


class TestClassifyVariance:
    def test_perfect(self):
        assert classify_variance(3.0) == "PERFECT ESTIMATE"

    def test_controlled(self):
        assert classify_variance(8.0) == "Controlled"

    def test_moderate(self):
        assert classify_variance(15.0) == "Moderate"

    def test_high_risk(self):
        assert classify_variance(25.0) == "High Risk"
