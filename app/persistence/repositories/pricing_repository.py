"""
Apeiron CostEstimation Pro – Pricing Repository
================================================
All database operations for StackCost, InfraCost, and PricingStrategy entities.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import StackCost, InfraCost, PricingStrategy


class PricingRepository(BaseRepository):
    """Repository for pricing-related CRUD operations."""

    # ── Stack Costs ──
    def get_all_stack_costs(self) -> list[StackCost]:
        return self.session.query(StackCost).all()

    def create_stack_cost(self, **kwargs) -> StackCost:
        sc = StackCost(**kwargs)
        self.session.add(sc)
        self.session.commit()
        return sc

    def update_stack_cost(self, stack_id: int, **kwargs) -> StackCost | None:
        sc = self.session.query(StackCost).filter_by(id=stack_id).first()
        if not sc:
            return None
        for key, val in kwargs.items():
            setattr(sc, key, val)
        self.session.commit()
        return sc

    def delete_stack_cost(self, stack_id: int) -> bool:
        sc = self.session.query(StackCost).filter_by(id=stack_id).first()
        if not sc:
            return False
        self.session.delete(sc)
        self.session.commit()
        return True

    # ── Infra Costs ──
    def get_all_infra_costs(self) -> list[InfraCost]:
        return self.session.query(InfraCost).all()

    def create_infra_cost(self, **kwargs) -> InfraCost:
        ic = InfraCost(**kwargs)
        self.session.add(ic)
        self.session.commit()
        return ic

    def update_infra_cost(self, infra_id: int, **kwargs) -> InfraCost | None:
        ic = self.session.query(InfraCost).filter_by(id=infra_id).first()
        if not ic:
            return None
        for key, val in kwargs.items():
            setattr(ic, key, val)
        self.session.commit()
        return ic

    def delete_infra_cost(self, infra_id: int) -> bool:
        ic = self.session.query(InfraCost).filter_by(id=infra_id).first()
        if not ic:
            return False
        self.session.delete(ic)
        self.session.commit()
        return True

    # ── Pricing Strategies ──
    def get_all_pricing_strategies(self) -> list[PricingStrategy]:
        return self.session.query(PricingStrategy).all()

    def get_pricing_strategy(self, name: str) -> PricingStrategy | None:
        return self.session.query(PricingStrategy).filter_by(name=name).first()

    def create_pricing_strategy(self, **kwargs) -> PricingStrategy:
        ps = PricingStrategy(**kwargs)
        self.session.add(ps)
        self.session.commit()
        return ps

    def delete_pricing_strategy(self, strategy_id: int) -> bool:
        ps = self.session.query(PricingStrategy).filter_by(id=strategy_id).first()
        if not ps:
            return False
        self.session.delete(ps)
        self.session.commit()
        return True
