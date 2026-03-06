"""
Apeiron CostEstimation Pro – Preset Repository
===============================================
All database operations for IndustryPreset, IndustryPresetModule,
and SystemLookup entities.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import IndustryPreset, IndustryPresetModule, SystemLookup


class PresetRepository(BaseRepository):
    """Repository for industry presets and system lookups."""

    # ── Industry Presets ──
    def get_all_presets(self) -> list[IndustryPreset]:
        return self.session.query(IndustryPreset).all()

    def get_preset_with_modules(self, preset_id: int) -> IndustryPreset | None:
        return self.session.query(IndustryPreset).filter_by(id=preset_id).first()

    def create_preset(self, name: str, modules: list[dict] | None = None) -> IndustryPreset:
        preset = IndustryPreset(name=name)
        self.session.add(preset)
        self.session.flush()
        if modules:
            for mod in modules:
                self.session.add(IndustryPresetModule(
                    preset_id=preset.id,
                    name=mod["name"],
                    default_hours=mod.get("default_hours", 0),
                ))
        self.session.commit()
        return preset

    def delete_preset(self, preset_id: int) -> bool:
        preset = self.session.query(IndustryPreset).filter_by(id=preset_id).first()
        if not preset:
            return False
        self.session.delete(preset)
        self.session.commit()
        return True

    # ── System Lookups ──
    def get_lookup_values(self, category: str) -> list[str]:
        items = self.session.query(SystemLookup).filter_by(category=category).all()
        return [item.value for item in items]

    def get_all_lookups(self) -> list[SystemLookup]:
        return self.session.query(SystemLookup).all()

    def add_lookup_value(self, category: str, value: str) -> SystemLookup:
        item = SystemLookup(category=category, value=value)
        self.session.add(item)
        self.session.commit()
        return item

    def delete_lookup_value(self, lookup_id: int) -> bool:
        item = self.session.query(SystemLookup).filter_by(id=lookup_id).first()
        if not item:
            return False
        self.session.delete(item)
        self.session.commit()
        return True
