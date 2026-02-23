"""
Apeiron CostEstimation Pro – Financial Logic Engine (Layer 1)
=============================================================
Core estimation calculations: effort, cost, risk, stage distribution,
maintenance forecasting, variance tracking.
"""

from datetime import datetime
from app.models import (
    Employee, Project, ProjectModule, Estimate,
    MaintenanceRecord, AuditLog
)

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────
COMPLEXITY_MULTIPLIERS = {
    "Simple": 0.8,
    "Medium": 1.0,
    "Complex": 1.3,
    "Enterprise": 1.6,
}

APP_TYPE_ADJUSTMENTS = {
    "Social Media": 1.1,
    "E-commerce": 1.15,
    "Gaming": 1.25,
    "Education": 0.95,
    "Healthcare": 1.2,
    "Travel": 1.05,
    "Productivity": 1.0,
    "On-demand": 1.1,
    "AI": 1.35,
}

DEFAULT_STAGES = {
    "Planning": 10.0,
    "Design": 15.0,
    "Development": 60.0,
    "Testing": 10.0,
    "Deployment": 5.0,
}

VARIANCE_THRESHOLDS = {
    "PERFECT ESTIMATE": 5.0,
    "Controlled": 10.0,
    "Moderate": 20.0,
    # Anything above 20% is "High Risk"
}

# ──────────────────────────────────────────────
# INDUSTRY PRESETS
# ──────────────────────────────────────────────
INDUSTRY_PRESETS = {
    "SME CRM": {
        "app_type": "Productivity",
        "complexity": "Medium",
        "modules": [
            {"name": "User Management & Auth", "hours": 80},
            {"name": "Dashboard & Analytics", "hours": 100},
            {"name": "Contact Management", "hours": 80},
            {"name": "Reports & Export", "hours": 60},
            {"name": "Settings & Configuration", "hours": 40},
            {"name": "Notifications", "hours": 40},
            {"name": "API Integration Layer", "hours": 80},
        ],
    },
    "Industrial Compliance": {
        "app_type": "Healthcare",
        "complexity": "Complex",
        "modules": [
            {"name": "Audit Log Engine", "hours": 120},
            {"name": "Compliance Rule Engine", "hours": 160},
            {"name": "Document Management", "hours": 100},
            {"name": "Reporting & Dashboards", "hours": 80},
            {"name": "User & Role Management", "hours": 60},
            {"name": "Alert & Notification System", "hours": 60},
            {"name": "Integration & API Layer", "hours": 60},
        ],
    },
    "Logistics Platform": {
        "app_type": "On-demand",
        "complexity": "Complex",
        "modules": [
            {"name": "Fleet Management", "hours": 140},
            {"name": "Route Optimization", "hours": 120},
            {"name": "Real-time Tracking", "hours": 100},
            {"name": "Invoicing & Billing", "hours": 80},
            {"name": "Warehouse Management", "hours": 100},
            {"name": "Driver App Module", "hours": 80},
            {"name": "Admin Dashboard", "hours": 100},
        ],
    },
    "AI Chatbot": {
        "app_type": "AI",
        "complexity": "Complex",
        "modules": [
            {"name": "NLP Processing Engine", "hours": 160},
            {"name": "Training Data Pipeline", "hours": 120},
            {"name": "Chat UI & Widget", "hours": 80},
            {"name": "Analytics & Insights", "hours": 80},
            {"name": "Integration APIs", "hours": 60},
            {"name": "Admin & Config Panel", "hours": 60},
        ],
    },
    "E-commerce Standard": {
        "app_type": "E-commerce",
        "complexity": "Medium",
        "modules": [
            {"name": "Product Catalog", "hours": 100},
            {"name": "Shopping Cart & Checkout", "hours": 80},
            {"name": "Payment Gateway", "hours": 80},
            {"name": "Order Management", "hours": 80},
            {"name": "Admin Dashboard", "hours": 80},
            {"name": "User Accounts & Reviews", "hours": 60},
            {"name": "Search & Filters", "hours": 60},
            {"name": "Inventory Management", "hours": 60},
        ],
    },
    "SaaS MVP": {
        "app_type": "Productivity",
        "complexity": "Simple",
        "modules": [
            {"name": "Auth & Onboarding", "hours": 60},
            {"name": "Core Dashboard", "hours": 80},
            {"name": "Subscription & Billing", "hours": 80},
            {"name": "REST API Layer", "hours": 60},
            {"name": "Landing Page & Docs", "hours": 40},
            {"name": "Settings & Profile", "hours": 40},
            {"name": "Admin Panel", "hours": 40},
        ],
    },
}

# ──────────────────────────────────────────────
# PRICING PSYCHOLOGY MODES
# ──────────────────────────────────────────────
PRICING_MODES = {
    "Competitive": {
        "description": "Win on price – lean margins",
        "profit_pct": 10.0,
        "risk_pct": 5.0,
        "maintenance_buffer_pct": 10.0,
    },
    "Value-Based": {
        "description": "Balanced cost & perceived value",
        "profit_pct": 25.0,
        "risk_pct": 10.0,
        "maintenance_buffer_pct": 15.0,
    },
    "Aggressive Bid": {
        "description": "Near-cost pricing to win deal",
        "profit_pct": 5.0,
        "risk_pct": 5.0,
        "maintenance_buffer_pct": 8.0,
    },
    "Premium Enterprise": {
        "description": "High-touch premium positioning",
        "profit_pct": 40.0,
        "risk_pct": 15.0,
        "maintenance_buffer_pct": 20.0,
    },
}


# ──────────────────────────────────────────────
# EMPLOYEE COST HELPERS
# ──────────────────────────────────────────────
def calculate_employee_costs(employee: Employee) -> Employee:
    """
    Recalculate real monthly cost and hourly rate.
    Real Monthly = Base × (1 + total_pct/100)
    Hourly = Real Monthly / 22 / 8
    """
    employee.recalculate_costs()
    return employee


def compute_hourly_from_salary(
    base_salary: float,
    pf_pct: float = 12.0,
    bonus_pct: float = 8.33,
    leave_pct: float = 4.0,
    infra_pct: float = 5.0,
    admin_pct: float = 3.0,
) -> dict:
    """
    Standalone calculation without DB objects.
    Returns dict with real_monthly_cost and hourly_cost.
    """
    total_pct = pf_pct + bonus_pct + leave_pct + infra_pct + admin_pct
    real_monthly = round(base_salary * (1 + total_pct / 100), 2)
    hourly = round(real_monthly / 22 / 8, 2)
    return {
        "total_add_on_pct": total_pct,
        "real_monthly_cost": real_monthly,
        "hourly_cost": hourly,
    }


# ──────────────────────────────────────────────
# EFFORT & LABOR COST
# ──────────────────────────────────────────────
def get_complexity_multiplier(complexity: str) -> float:
    """Return the baseline effort multiplier for given complexity."""
    return COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)


def get_app_type_adjustment(app_type: str) -> float:
    """Return the app-type effort adjustment factor."""
    return APP_TYPE_ADJUSTMENTS.get(app_type, 1.0)


def calculate_module_cost(module: ProjectModule, region_multiplier: float = 1.0) -> float:
    """
    Module cost = hourly_rate × estimated_hours × region_multiplier
    Uses hourly_rate_override if set, else employee's hourly_cost.
    """
    rate = module.hourly_rate_override
    if rate is None and module.employee:
        rate = module.employee.hourly_cost
    if rate is None:
        rate = 0.0

    cost = round(rate * module.estimated_hours * region_multiplier, 2)
    module.cost = cost
    return cost


def calculate_total_labor_cost(
    modules: list,
    complexity: str = "Medium",
    app_type: str = "Productivity",
    region_multiplier: float = 1.0,
) -> dict:
    """
    Total Labor Cost = Σ(module_cost) × complexity_mult × app_type_adj
    Returns breakdown dict.
    """
    raw_total = 0.0
    module_costs = []
    for mod in modules:
        mc = calculate_module_cost(mod, region_multiplier)
        module_costs.append({"name": mod.name, "hours": mod.estimated_hours, "cost": mc})
        raw_total += mc

    cx_mult = get_complexity_multiplier(complexity)
    app_adj = get_app_type_adjustment(app_type)
    adjusted_total = round(raw_total * cx_mult * app_adj, 2)

    return {
        "module_costs": module_costs,
        "raw_labor_total": raw_total,
        "complexity_multiplier": cx_mult,
        "app_type_adjustment": app_adj,
        "adjusted_labor_total": adjusted_total,
    }


# ──────────────────────────────────────────────
# TOTAL HOURS & PERSON-MONTHS
# ──────────────────────────────────────────────
def calculate_total_hours(modules: list) -> float:
    """Sum of estimated hours across all modules."""
    return sum(m.estimated_hours for m in modules)


def hours_to_person_months(hours: float) -> float:
    """Convert hours to person-months (22 days × 8 hours = 176)."""
    if hours <= 0:
        return 0.0
    return round(hours / 176, 2)


# ──────────────────────────────────────────────
# STAGE DISTRIBUTION
# ──────────────────────────────────────────────
def calculate_stage_distribution(
    total_cost: float,
    planning_pct: float = 10.0,
    design_pct: float = 15.0,
    development_pct: float = 60.0,
    testing_pct: float = 10.0,
    deployment_pct: float = 5.0,
) -> dict:
    """
    Distribute total cost across project stages by percentage.
    Returns dict: stage_name → cost.
    """
    stages = {
        "Planning": planning_pct,
        "Design": design_pct,
        "Development": development_pct,
        "Testing": testing_pct,
        "Deployment": deployment_pct,
    }
    distribution = {}
    for stage, pct in stages.items():
        distribution[stage] = round(total_cost * pct / 100, 2)
    return distribution


# ──────────────────────────────────────────────
# INFRASTRUCTURE & STACK COSTS
# ──────────────────────────────────────────────
def calculate_infra_stack_total(infra_items: list, stack_items: list) -> dict:
    """
    Sum all infra and stack costs.
    Items are model objects with .cost attribute.
    """
    infra_total = sum(item.cost for item in infra_items)
    stack_total = sum(item.cost for item in stack_items)
    return {
        "infra_total": round(infra_total, 2),
        "stack_total": round(stack_total, 2),
        "combined_total": round(infra_total + stack_total, 2),
    }


# ──────────────────────────────────────────────
# RISK & BUFFER
# ──────────────────────────────────────────────
def calculate_risk_buffer(
    gross_cost: float,
    maintenance_buffer_pct: float = 15.0,
    risk_contingency_pct: float = 10.0,
) -> dict:
    """
    Safe Cost = Gross Cost + Maintenance Buffer + Risk Contingency.
    """
    maintenance_buffer = round(gross_cost * maintenance_buffer_pct / 100, 2)
    risk_contingency = round(gross_cost * risk_contingency_pct / 100, 2)
    safe_cost = round(gross_cost + maintenance_buffer + risk_contingency, 2)
    return {
        "gross_cost": gross_cost,
        "maintenance_buffer": maintenance_buffer,
        "risk_contingency": risk_contingency,
        "safe_cost": safe_cost,
    }


# ──────────────────────────────────────────────
# PROFIT & FINAL PRICE
# ──────────────────────────────────────────────
def calculate_final_price(safe_cost: float, profit_margin_pct: float = 20.0) -> dict:
    """
    Final Price = Safe Cost + Profit.
    """
    profit = round(safe_cost * profit_margin_pct / 100, 2)
    final = round(safe_cost + profit, 2)
    return {
        "safe_cost": safe_cost,
        "profit_amount": profit,
        "profit_margin_pct": profit_margin_pct,
        "final_price": final,
    }


# ──────────────────────────────────────────────
# MAINTENANCE FORECAST
# ──────────────────────────────────────────────
def calculate_maintenance_forecast(
    development_cost: float,
    annual_pct: float = 15.0,
    years: int = 5,
) -> list:
    """
    Annual Maintenance = annual_pct% of Development Cost.
    Returns list of dicts per year.
    """
    annual = round(development_cost * annual_pct / 100, 2)
    forecast = []
    for y in range(1, years + 1):
        forecast.append({
            "year": y,
            "annual_cost": annual,
            "cumulative_cost": round(annual * y, 2),
        })
    return forecast


# ──────────────────────────────────────────────
# VARIANCE / PERFECT ESTIMATE
# ──────────────────────────────────────────────
def calculate_variance(estimated: float, actual: float) -> dict:
    """
    Variance = |Actual – Estimated| / Estimated × 100.
    Classify the result.
    """
    if estimated <= 0:
        return {
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


# ──────────────────────────────────────────────
# ANALYTICS
# ──────────────────────────────────────────────
def cost_per_function_point(total_cost: float, function_points: int) -> float:
    """Cost per function point. Returns 0 if no FPs."""
    if function_points <= 0:
        return 0.0
    return round(total_cost / function_points, 2)


def burn_rate_monthly(total_cost: float, duration_months: float) -> float:
    """Monthly burn rate = total / duration."""
    if duration_months <= 0:
        return 0.0
    return round(total_cost / duration_months, 2)


def revenue_margin(final_price: float, safe_cost: float) -> float:
    """Revenue Margin % = (Revenue - Cost) / Revenue × 100."""
    if final_price <= 0:
        return 0.0
    return round((final_price - safe_cost) / final_price * 100, 2)


def contribution_margin(final_price: float, variable_cost: float) -> float:
    """Contribution Margin = Final Price - Variable Cost."""
    return round(final_price - variable_cost, 2)


# ──────────────────────────────────────────────
# FULL PROJECT ESTIMATION (ORCHESTRATOR)
# ──────────────────────────────────────────────
def run_full_estimation(
    modules: list,
    complexity: str,
    app_type: str,
    region_multiplier: float,
    infra_items: list,
    stack_items: list,
    maintenance_buffer_pct: float,
    risk_contingency_pct: float,
    profit_margin_pct: float,
    stage_pcts: dict = None,
    function_points: int = 0,
    estimated_duration_months: float = 0.0,
    maintenance_years: int = 5,
    maintenance_annual_pct: float = 15.0,
) -> dict:
    """
    Run the complete estimation pipeline and return all results.
    """
    # 1. Labor
    labor = calculate_total_labor_cost(modules, complexity, app_type, region_multiplier)

    # 2. Infra + Stack
    infra_stack = calculate_infra_stack_total(infra_items, stack_items)

    # 3. Gross cost
    gross_cost = round(labor["adjusted_labor_total"] + infra_stack["combined_total"], 2)

    # 4. Risk & buffer
    risk = calculate_risk_buffer(gross_cost, maintenance_buffer_pct, risk_contingency_pct)

    # 5. Profit & final
    final = calculate_final_price(risk["safe_cost"], profit_margin_pct)

    # 6. Stage distribution
    sp = stage_pcts or DEFAULT_STAGES
    stages = calculate_stage_distribution(
        labor["adjusted_labor_total"],
        sp.get("Planning", 10), sp.get("Design", 15),
        sp.get("Development", 60), sp.get("Testing", 10),
        sp.get("Deployment", 5),
    )

    # 7. Maintenance
    dev_cost = stages.get("Development", 0)
    maintenance = calculate_maintenance_forecast(dev_cost, maintenance_annual_pct, maintenance_years)

    # 8. Analytics
    total_hours = calculate_total_hours(modules)
    cpfp = cost_per_function_point(final["final_price"], function_points)
    br = burn_rate_monthly(final["final_price"], estimated_duration_months)
    rm = revenue_margin(final["final_price"], risk["safe_cost"])
    pm = hours_to_person_months(total_hours)

    return {
        "labor": labor,
        "infra_stack": infra_stack,
        "gross_cost": gross_cost,
        "risk_buffer": risk,
        "final_pricing": final,
        "stage_distribution": stages,
        "maintenance_forecast": maintenance,
        "analytics": {
            "total_hours": total_hours,
            "person_months": pm,
            "cost_per_function_point": cpfp,
            "burn_rate_monthly": br,
            "revenue_margin_pct": rm,
        },
    }


# ──────────────────────────────────────────────
# CURRENCY FORMATTING
# ──────────────────────────────────────────────
def format_inr(amount: float) -> str:
    """Format amount in Indian Rupees with commas (₹1,23,456.78)."""
    if amount < 0:
        return f"-₹{format_inr(-amount)[1:]}"
    # Indian number system: last 3 digits, then groups of 2
    s = f"{amount:,.2f}"
    parts = s.split(".")
    integer_part = parts[0].replace(",", "")
    decimal_part = parts[1] if len(parts) > 1 else "00"

    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last_three = integer_part[-3:]
        rest = integer_part[:-3]
        # Group in twos from right
        groups = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(groups) + "," + last_three

    return f"₹{formatted}.{decimal_part}"


# ──────────────────────────────────────────────
# AUDIT LOGGING
# ──────────────────────────────────────────────
def create_audit_entry(
    session,
    table_name: str,
    record_id: int,
    action: str,
    field_name: str = "",
    old_value: str = "",
    new_value: str = "",
):
    """Write an audit log entry."""
    entry = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        field_name=field_name,
        old_value=str(old_value),
        new_value=str(new_value),
    )
    session.add(entry)
    session.commit()
