# Apeiron CostEstimation Pro

A fully offline desktop **Software Cost Estimation System** for TechLogix, built with Python, PyQt6, SQLite, and ReportLab.

## Features

- **Employee Cost Modeling** – Real monthly cost and hourly rate calculation
- **Effort Estimation** – Module-based labor cost with complexity & app-type multipliers
- **Stage Distribution** – Automatic cost allocation across project phases
- **Risk & Buffer** – Maintenance buffer, risk contingency, and profit margin
- **Maintenance Forecast** – Multi-year projection (1–5 years)
- **Region-Based Pricing** – Hourly multipliers for India, NA, EU, Asia
- **Estimated vs Actual** – Variance tracking with PERFECT ESTIMATE detection
- **Client Proposal PDF** – Professional export hiding internal costs
- **Audit Trail** – All financial edits are logged
- **Analytics** – Cost/FP, burn rate, revenue margin, contribution margin

## Requirements

- **OS**: Ubuntu 24.04 (or any Linux with Python 3.11+)
- **Python**: 3.11+

## Setup

```bash
# 1. Clone or navigate to project directory
cd apeiron_cost_estimation_pro

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python3 run.py
```

## Build Standalone Executable

```bash
# Ensure venv is activated
python build.py
# Executable → dist/ApeironCostEstimationPro
```

## Run Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```text
apeiron_cost_estimation_pro/
├── run.py                  # Entry point
├── build.py                # PyInstaller build script
├── requirements.txt        # Dependencies
├── README.md
├── app/
│   ├── __init__.py         # App metadata
│   ├── models.py           # SQLAlchemy ORM models
│   ├── database.py         # DB engine, session, init
│   ├── logic.py            # Layer 1 – Financial engine
│   ├── proposal_generator.py  # Layer 2 – PDF proposal
│   └── main_ui.py          # PyQt6 UI (4 tabs)
├── assets/                 # Branding assets (optional)
└── tests/
    ├── __init__.py
    └── test_logic.py       # Unit tests for financial formulas
```

## Database

SQLite database is auto-created at:

```text
~/.apeiron_costpro/costpro.db
```

## License

Proprietary – TechLogix
