# Apeiron CostEstimation Pro

A fully offline, desktop-based **Software Cost Estimation System** built for TechLogix. It is engineered with Python, PyQt6, SQLite, and ReportLab to provide a robust, data-driven quoting tool for modern software agencies.

## Features & Capabilities

### Level 1: Core Financial Engine

- **Employee Cost Modeling** – Real monthly cost and hourly rate calculation, factoring in PF, Bonus, Leave, Infra, and Admin percentages.
- **Effort Estimation** – Module-based labor cost estimation with Complexity and App-Type modifiers.
- **Stage Distribution** – Automatic cost allocation across project phases (Planning, Design, Development, Testing, Deployment).
- **Region-Based Pricing** – Variable multipliers for geographic zones (India, NA, EU, Asia).
- **Client Proposal Export** – Professional PDF generation that hides internal costs and only exposes required client-facing metrics.
- **Audit Trail** – All financial configuration edits are audited and logged.

### Level 2: Advanced Visualization & Strategy

- **Financial Analytics Dashboard** – Interactive Matplotlib charts tracking stage distribution (Pie), module costs (Bar), variance (Bar), and maintenance forecasting (Line).
- **Industry Presets** – Rapidly scaffold quotes using predefined module templates (e.g., SME CRM, SaaS MVP, AI Chatbot).
- **Pricing Psychology** – Four built-in pricing modes (Competitive, Value-Based, Aggressive Bid, Premium Enterprise) to instantly adjust risk constraints and profit margins.
- **Corporate Branding Engine** – A professional UI with "Deep Blue" and "True Light" themes, SVG-style headers, and clean typographical hierarchy.
- **SOP Guide** – A detachable graphical Standard Operating Procedure window.

### Level 3: Dynamic System Configuration

- **Database-Driven Architecture** – All configuration maps (Employee Roles, Stack Categories, App Types, Complexities, Pricing Strategies, Presets) are handled dynamically in SQLite.
- **System Configuration UI** – A dedicated Master Data tab providing complete CRUD control over all multipliers and application parameters.
- **Live Sync** – Dropdowns and estimation algorithms update in real-time when system models are altered.

## Requirements

- **OS**: Ubuntu 24.04 (or any Linux with Python 3.11+)
- **Python**: 3.11+

## Setup & Installation

```bash
# 1. Clone or navigate to the project directory
cd apeiron_cost_estimation_pro

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python3 run.py
```

## Running the Application

When starting for the first time, the application will automatically create the SQLite database at `~/.apeiron_costpro/costpro.db` and securely seed defaults for the dynamic configuration parameters.

```bash
python3 run.py
```

## Run Tests

The application includes a comprehensive Pytest suite mocking the database to verify financial integrity.

```bash
python3 -m pytest tests/ -v
```

## License

Proprietary – TechLogix
