"""
Apeiron CostEstimation Pro – Domain Constants
==============================================
All business constants, defaults, and thresholds.
Pure values – no imports from other app layers.
"""

# ──────────────────────────────────────────────
# WORKING TIME CONSTANTS
# ──────────────────────────────────────────────
WORKING_DAYS_PER_MONTH = 22
WORKING_HOURS_PER_DAY = 8
HOURS_PER_PERSON_MONTH = WORKING_DAYS_PER_MONTH * WORKING_HOURS_PER_DAY  # 176

# ──────────────────────────────────────────────
# DEFAULT ADD-ON PERCENTAGES (Employee cost)
# ──────────────────────────────────────────────
DEFAULT_PF_PCT = 12.0
DEFAULT_BONUS_PCT = 8.33
DEFAULT_LEAVE_PCT = 4.0
DEFAULT_INFRA_PCT = 5.0
DEFAULT_ADMIN_PCT = 3.0

# ──────────────────────────────────────────────
# DEFAULT RISK / PROFIT / MAINTENANCE
# ──────────────────────────────────────────────
DEFAULT_MAINTENANCE_PCT = 15.0
DEFAULT_RISK_PCT = 10.0
DEFAULT_PROFIT_PCT = 20.0

# ──────────────────────────────────────────────
# DEFAULT STAGE DISTRIBUTION (percentages)
# ──────────────────────────────────────────────
DEFAULT_STAGES = {
    "Planning": 10.0,
    "Design": 15.0,
    "Development": 60.0,
    "Testing": 10.0,
    "Deployment": 5.0,
}

# ──────────────────────────────────────────────
# VARIANCE THRESHOLDS
# ──────────────────────────────────────────────
VARIANCE_THRESHOLDS = {
    "PERFECT ESTIMATE": 5.0,
    "Controlled": 10.0,
    "Moderate": 20.0,
    # Anything above 20% is "High Risk"
}
