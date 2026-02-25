"""
Apeiron CostEstimation Pro – Database Setup
============================================
SQLite initialization, session management, and seed data.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base, RegionMultiplier, SystemLookup, AppTypeMultiplier,
    ComplexityMultiplier, PricingStrategy, IndustryPreset, IndustryPresetModule
)

# ──────────────────────────────────────────────
# DEFAULT SEED DATA
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
# DATABASE PATH
# ──────────────────────────────────────────────
DB_DIR = os.path.join(os.path.expanduser("~"), ".apeiron_costpro")
DB_PATH = os.path.join(DB_DIR, "costpro.db")
DB_URL = f"sqlite:///{DB_PATH}"


def get_engine():
    """Create and return a SQLAlchemy engine."""
    os.makedirs(DB_DIR, exist_ok=True)
    engine = create_engine(DB_URL, echo=False)
    return engine


def get_session():
    """Return a new database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """
    Create all tables if they don't exist.
    Seed default region multipliers and dynamic config.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
    _seed_defaults(engine)
    _seed_system_config(engine)
    return engine


def _seed_defaults(engine):
    """Insert default region multipliers if table is empty."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        count = session.query(RegionMultiplier).count()
        if count == 0:
            defaults = [
                RegionMultiplier(region_name="India", multiplier=1.0),
                RegionMultiplier(region_name="North America", multiplier=4.0),
                RegionMultiplier(region_name="Western Europe", multiplier=3.5),
                RegionMultiplier(region_name="Eastern Europe", multiplier=2.0),
                RegionMultiplier(region_name="Asia", multiplier=1.5),
            ]
            session.add_all(defaults)
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def _seed_system_config(engine):
    """Seed dynamic configuration tables from legacy Python constants if empty."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # 1. System Lookups (Roles, Categories)
        if session.query(SystemLookup).count() == 0:
            lookups = [
                ("role", "Project Manager"), ("role", "Architect"), ("role", "Frontend Developer"),
                ("role", "Backend Developer"), ("role", "DevOps Engineer"), ("role", "QA Tester"),
                ("role", "UI/UX Designer"), ("role", "Scrum Master"),
                ("infra_category", "Hosting"), ("infra_category", "Database"), ("infra_category", "API Integration"),
                ("infra_category", "Security"), ("infra_category", "App Store Fees"), ("infra_category", "Marketing"),
                ("infra_category", "DevOps"), ("infra_category", "Other"),
                ("stack_category", "Frontend"), ("stack_category", "Backend"), ("stack_category", "Database"),
                ("stack_category", "DevOps"), ("stack_category", "Analytics"), ("stack_category", "Third-party APIs"),
                ("stack_category", "Other"),
                ("billing_type", "one_time"), ("billing_type", "monthly"), ("billing_type", "yearly"), ("billing_type", "usage_based")
            ]
            for cat, val in lookups:
                session.add(SystemLookup(category=cat, value=val))
        
        # 2. App Type Multipliers
        if session.query(AppTypeMultiplier).count() == 0:
            for name, mult in APP_TYPE_ADJUSTMENTS.items():
                session.add(AppTypeMultiplier(name=name, multiplier=mult))
                
        # 3. Complexity Multipliers
        if session.query(ComplexityMultiplier).count() == 0:
            for name, mult in COMPLEXITY_MULTIPLIERS.items():
                session.add(ComplexityMultiplier(name=name, multiplier=mult))
                
        # 4. Pricing Strategies
        if session.query(PricingStrategy).count() == 0:
            for name, data in PRICING_MODES.items():
                session.add(PricingStrategy(
                    name=name,
                    profit_margin_pct=data["profit_pct"],
                    risk_contingency_pct=data["risk_pct"],
                    description=data["description"]
                ))
                
        # 5. Industry Presets
        if session.query(IndustryPreset).count() == 0:
            for name, data in INDUSTRY_PRESETS.items():
                preset = IndustryPreset(name=name)
                session.add(preset)
                session.flush() # get ID
                for mod in data["modules"]:
                    session.add(IndustryPresetModule(
                        preset_id=preset.id,
                        name=mod["name"],
                        default_hours=mod["hours"]
                    ))
                    
        session.commit()
    except Exception as e:
        print("Error seeding system config:", e)
        session.rollback()
    finally:
        session.close()
