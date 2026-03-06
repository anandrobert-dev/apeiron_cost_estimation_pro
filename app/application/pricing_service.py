"""
Apeiron CostEstimation Pro – Pricing Service
=============================================
Use case: Manage multipliers, pricing strategies, stack/infra costs.
Imports: Persistence (multiplier_repository, pricing_repository, preset_repository).
"""

from app.persistence.repositories.multiplier_repository import MultiplierRepository
from app.persistence.repositories.pricing_repository import PricingRepository
from app.persistence.repositories.preset_repository import PresetRepository


class PricingService:
    """Orchestrates multiplier and pricing configuration."""

    def __init__(
        self,
        multiplier_repo: MultiplierRepository,
        pricing_repo: PricingRepository,
        preset_repo: PresetRepository,
    ):
        self.mult = multiplier_repo
        self.pricing = pricing_repo
        self.preset = preset_repo

    # ── Complexity ──
    def get_all_complexity(self) -> list[dict]:
        return [{"id": c.id, "name": c.name, "multiplier": c.multiplier}
                for c in self.mult.get_all_complexity()]

    def upsert_complexity(self, name: str, multiplier: float) -> dict:
        rec = self.mult.upsert_complexity(name, multiplier)
        return {"id": rec.id, "name": rec.name, "multiplier": rec.multiplier}

    # ── App Type ──
    def get_all_app_types(self) -> list[dict]:
        return [{"id": a.id, "name": a.name, "multiplier": a.multiplier}
                for a in self.mult.get_all_app_types()]

    def upsert_app_type(self, name: str, multiplier: float) -> dict:
        rec = self.mult.upsert_app_type(name, multiplier)
        return {"id": rec.id, "name": rec.name, "multiplier": rec.multiplier}

    # ── Regions ──
    def get_all_regions(self) -> list[dict]:
        return [{"id": r.id, "region_name": r.region_name, "multiplier": r.multiplier}
                for r in self.mult.get_all_regions()]

    # ── Pricing Strategies ──
    def get_all_pricing_strategies(self) -> list[dict]:
        return [
            {
                "id": ps.id,
                "name": ps.name,
                "profit_margin_pct": ps.profit_margin_pct,
                "risk_contingency_pct": ps.risk_contingency_pct,
                "description": ps.description,
            }
            for ps in self.pricing.get_all_pricing_strategies()
        ]

    # ── Stack Costs ──
    def get_all_stack_costs(self) -> list[dict]:
        return [
            {"id": s.id, "name": s.name, "category": s.category,
             "cost": s.cost, "billing_type": s.billing_type}
            for s in self.pricing.get_all_stack_costs()
        ]

    def create_stack_cost(self, **kwargs) -> dict:
        sc = self.pricing.create_stack_cost(**kwargs)
        return {"id": sc.id, "name": sc.name, "cost": sc.cost, "billing_type": sc.billing_type}

    def delete_stack_cost(self, stack_id: int) -> bool:
        return self.pricing.delete_stack_cost(stack_id)

    # ── Infra Costs ──
    def get_all_infra_costs(self) -> list[dict]:
        return [
            {"id": i.id, "name": i.name, "category": i.category,
             "cost": i.cost, "billing_type": i.billing_type}
            for i in self.pricing.get_all_infra_costs()
        ]

    def create_infra_cost(self, **kwargs) -> dict:
        ic = self.pricing.create_infra_cost(**kwargs)
        return {"id": ic.id, "name": ic.name, "cost": ic.cost, "billing_type": ic.billing_type}

    def delete_infra_cost(self, infra_id: int) -> bool:
        return self.pricing.delete_infra_cost(infra_id)

    # ── Presets ──
    def get_all_presets(self) -> list[dict]:
        return [{"id": p.id, "name": p.name} for p in self.preset.get_all_presets()]

    def get_preset_with_modules(self, preset_id: int) -> dict | None:
        p = self.preset.get_preset_with_modules(preset_id)
        if not p:
            return None
        return {
            "id": p.id,
            "name": p.name,
            "modules": [
                {"id": m.id, "name": m.name, "default_hours": m.default_hours}
                for m in p.modules
            ],
        }

    # ── System Lookups ──
    def get_lookup_values(self, category: str) -> list[str]:
        return self.preset.get_lookup_values(category)
