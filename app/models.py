"""
Apeiron CostEstimation Pro – SQLAlchemy ORM Models
===================================================
All database tables for the cost estimation system.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    DateTime, Date, ForeignKey, Enum as SAEnum, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ──────────────────────────────────────────────
# EMPLOYEE MASTER
# ──────────────────────────────────────────────
class Employee(Base):
    """Stores employee details including real cost calculation."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    role = Column(String(100), nullable=False)
    base_salary = Column(Float, nullable=False, default=0.0)

    # Percentage add-ons (stored as decimal, e.g. 12 = 12%)
    pf_pct = Column(Float, default=12.0)
    bonus_pct = Column(Float, default=8.33)
    leave_pct = Column(Float, default=4.0)
    infra_pct = Column(Float, default=5.0)
    admin_pct = Column(Float, default=3.0)

    # Computed fields (cached for speed)
    real_monthly_cost = Column(Float, default=0.0)
    hourly_cost = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def recalculate_costs(self):
        """
        Real Monthly Cost = Base × (1 + total_pct/100)
        Hourly Cost       = Real Monthly ÷ 22 days ÷ 8 hours
        """
        total_pct = (
            self.pf_pct + self.bonus_pct + self.leave_pct
            + self.infra_pct + self.admin_pct
        )
        self.real_monthly_cost = round(self.base_salary * (1 + total_pct / 100), 2)
        self.hourly_cost = round(self.real_monthly_cost / 22 / 8, 2)

    def __repr__(self):
        return f"<Employee {self.name} | {self.role} | ₹{self.hourly_cost}/hr>"


# ──────────────────────────────────────────────
# REGION MULTIPLIERS
# ──────────────────────────────────────────────
class RegionMultiplier(Base):
    """Hourly rate multipliers by geography."""
    __tablename__ = "region_multipliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(100), nullable=False, unique=True)
    multiplier = Column(Float, nullable=False, default=1.0)

    def __repr__(self):
        return f"<Region {self.region_name} ×{self.multiplier}>"


# ──────────────────────────────────────────────
# STACK COST MASTER
# ──────────────────────────────────────────────
class StackCost(Base):
    """Technology stack license / tool costs."""
    __tablename__ = "stack_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="General")
    cost = Column(Float, default=0.0)
    billing_type = Column(
        String(20), default="one_time"
    )  # one_time | monthly | yearly | usage_based
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Stack {self.name} ₹{self.cost} ({self.billing_type})>"


# ──────────────────────────────────────────────
# INFRASTRUCTURE COST MASTER
# ──────────────────────────────────────────────
class InfraCost(Base):
    """Infrastructure & hidden costs (hosting, DB, APIs, marketing…)."""
    __tablename__ = "infra_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="General")
    cost = Column(Float, default=0.0)
    billing_type = Column(String(20), default="one_time")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Infra {self.name} ₹{self.cost} ({self.billing_type})>"


# ──────────────────────────────────────────────
# PROJECT
# ──────────────────────────────────────────────
class Project(Base):
    """Top-level project record."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    client_name = Column(String(300), default="")
    description = Column(Text, default="")

    app_type = Column(String(50), default="Productivity")
    # Social Media | E-commerce | Gaming | Education | Healthcare
    # Travel | Productivity | On-demand | AI

    complexity = Column(String(20), default="Medium")
    # Simple | Medium | Complex | Enterprise

    estimated_loc = Column(Integer, default=0)
    function_points = Column(Integer, default=0)

    region_id = Column(Integer, ForeignKey("region_multipliers.id"), nullable=True)
    region = relationship("RegionMultiplier")

    # Stage distribution overrides (percentages)
    stage_planning_pct = Column(Float, default=10.0)
    stage_design_pct = Column(Float, default=15.0)
    stage_development_pct = Column(Float, default=60.0)
    stage_testing_pct = Column(Float, default=10.0)
    stage_deployment_pct = Column(Float, default=5.0)

    # Risk & buffer overrides
    maintenance_buffer_pct = Column(Float, default=15.0)
    risk_contingency_pct = Column(Float, default=10.0)
    profit_margin_pct = Column(Float, default=20.0)

    # Timeline
    start_date = Column(Date, nullable=True)
    estimated_duration_months = Column(Float, default=0.0)

    # Status
    status = Column(String(20), default="draft")  # draft | active | completed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    modules = relationship("ProjectModule", back_populates="project",
                           cascade="all, delete-orphan")
    estimate = relationship("Estimate", back_populates="project", uselist=False,
                            cascade="all, delete-orphan")
    actual = relationship("Actual", back_populates="project", uselist=False,
                          cascade="all, delete-orphan")
    maintenance_records = relationship("MaintenanceRecord", back_populates="project",
                                       cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} [{self.complexity}]>"


# ──────────────────────────────────────────────
# PROJECT MODULES
# ──────────────────────────────────────────────
class ProjectModule(Base):
    """Individual modules within a project with effort allocation."""
    __tablename__ = "project_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text, default="")

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee")

    estimated_hours = Column(Float, default=0.0)
    hourly_rate_override = Column(Float, nullable=True)  # Optional override

    cost = Column(Float, default=0.0)  # Computed

    project = relationship("Project", back_populates="modules")

    def __repr__(self):
        return f"<Module {self.name} | {self.estimated_hours}h>"


# ──────────────────────────────────────────────
# ESTIMATES
# ──────────────────────────────────────────────
class Estimate(Base):
    """Captures the computed estimation snapshot for a project."""
    __tablename__ = "estimates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)

    total_labor_cost = Column(Float, default=0.0)
    total_infra_cost = Column(Float, default=0.0)
    total_stack_cost = Column(Float, default=0.0)
    gross_cost = Column(Float, default=0.0)

    maintenance_buffer = Column(Float, default=0.0)
    risk_contingency = Column(Float, default=0.0)
    safe_cost = Column(Float, default=0.0)

    profit_amount = Column(Float, default=0.0)
    final_price = Column(Float, default=0.0)

    cost_per_function_point = Column(Float, default=0.0)
    burn_rate_monthly = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="estimate")

    def __repr__(self):
        return f"<Estimate Project#{self.project_id} Safe=₹{self.safe_cost}>"


# ──────────────────────────────────────────────
# ACTUALS
# ──────────────────────────────────────────────
class Actual(Base):
    """Stores actual cost after project completion for variance analysis."""
    __tablename__ = "actuals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)

    actual_cost = Column(Float, default=0.0)
    actual_duration_months = Column(Float, default=0.0)
    completion_date = Column(Date, nullable=True)
    notes = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="actual")

    def __repr__(self):
        return f"<Actual Project#{self.project_id} ₹{self.actual_cost}>"


# ──────────────────────────────────────────────
# MAINTENANCE RECORDS
# ──────────────────────────────────────────────
class MaintenanceRecord(Base):
    """Multi-year maintenance projection records."""
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    year = Column(Integer, nullable=False)
    annual_cost = Column(Float, default=0.0)
    notes = Column(Text, default="")

    project = relationship("Project", back_populates="maintenance_records")

    def __repr__(self):
        return f"<Maintenance Project#{self.project_id} Y{self.year} ₹{self.annual_cost}>"


# ──────────────────────────────────────────────
# SYSTEM DYNAMIC CONFIGURATION
# ──────────────────────────────────────────────
class SystemLookup(Base):
    """Dynamic lists for UI dropdowns (Roles, Categories, etc)."""
    __tablename__ = "system_lookup"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)  # e.g., 'role', 'infra_category', 'stack_category', 'billing_type'
    value = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Lookup {self.category}: {self.value}>"


class AppTypeMultiplier(Base):
    """Multipliers for different kinds of applications."""
    __tablename__ = "app_type_multipliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    multiplier = Column(Float, nullable=False, default=1.0)
    
    def __repr__(self):
        return f"<AppType {self.name} ×{self.multiplier}>"


class ComplexityMultiplier(Base):
    """Multipliers for different architectural complexities."""
    __tablename__ = "complexity_multipliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    multiplier = Column(Float, nullable=False, default=1.0)

    def __repr__(self):
        return f"<Complexity {self.name} ×{self.multiplier}>"


class PricingStrategy(Base):
    """Configurable Pricing Psychology modes."""
    __tablename__ = "pricing_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    profit_margin_pct = Column(Float, nullable=False, default=20.0)
    risk_contingency_pct = Column(Float, nullable=False, default=10.0)
    description = Column(String(200), default="")

    def __repr__(self):
        return f"<Pricing {self.name}>"


class IndustryPreset(Base):
    """Groups of predefined modules for fast estimation."""
    __tablename__ = "industry_presets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    
    modules = relationship("IndustryPresetModule", back_populates="preset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Preset {self.name}>"


class IndustryPresetModule(Base):
    """Individual modules inside a preset template."""
    __tablename__ = "industry_preset_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    preset_id = Column(Integer, ForeignKey("industry_presets.id"), nullable=False)
    name = Column(String(200), nullable=False)
    default_hours = Column(Float, default=0.0)

    preset = relationship("IndustryPreset", back_populates="modules")

    def __repr__(self):
        return f"<PresetModule {self.name} | {self.default_hours}h>"


# ──────────────────────────────────────────────
# AUDIT LOG
# ──────────────────────────────────────────────
class AuditLog(Base):
    """Tracks financial edits for traceability."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # CREATE | UPDATE | DELETE
    field_name = Column(String(100), default="")
    old_value = Column(Text, default="")
    new_value = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Audit {self.action} {self.table_name}#{self.record_id}>"
