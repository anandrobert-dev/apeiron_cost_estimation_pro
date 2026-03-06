"""
Tests for MultiplierRepository.
"""

import pytest
from app.persistence.repositories.multiplier_repository import MultiplierRepository


class TestMultiplierRepository:

    def test_upsert_and_get_complexity(self, db_session):
        repo = MultiplierRepository(db_session)
        repo.upsert_complexity("Simple", 0.8)
        assert repo.get_complexity_multiplier("Simple") == 0.8

        # Update
        repo.upsert_complexity("Simple", 0.85)
        assert repo.get_complexity_multiplier("Simple") == 0.85

    def test_complexity_not_found(self, db_session):
        repo = MultiplierRepository(db_session)
        assert repo.get_complexity_multiplier("Unknown") == 1.0

    def test_get_all_complexity(self, db_session):
        repo = MultiplierRepository(db_session)
        repo.upsert_complexity("Simple", 0.8)
        repo.upsert_complexity("Medium", 1.0)
        repo.upsert_complexity("Complex", 1.4)
        assert len(repo.get_all_complexity()) == 3

    def test_delete_complexity(self, db_session):
        repo = MultiplierRepository(db_session)
        rec = repo.upsert_complexity("Old", 0.5)
        assert repo.delete_complexity(rec.id) is True
        assert repo.get_complexity_multiplier("Old") == 1.0

    def test_upsert_and_get_app_type(self, db_session):
        repo = MultiplierRepository(db_session)
        repo.upsert_app_type("E-commerce", 1.3)
        assert repo.get_app_type_multiplier("E-commerce") == 1.3

    def test_app_type_not_found(self, db_session):
        repo = MultiplierRepository(db_session)
        assert repo.get_app_type_multiplier("SomeApp") == 1.0

    def test_get_all_app_types(self, db_session):
        repo = MultiplierRepository(db_session)
        repo.upsert_app_type("A", 1.0)
        repo.upsert_app_type("B", 1.2)
        assert len(repo.get_all_app_types()) == 2

    def test_delete_app_type(self, db_session):
        repo = MultiplierRepository(db_session)
        rec = repo.upsert_app_type("ToDelete", 0.5)
        assert repo.delete_app_type(rec.id) is True

    def test_get_region_multiplier(self, db_session):
        from app.persistence.models import RegionMultiplier
        region = RegionMultiplier(region_name="US", multiplier=2.5)
        db_session.add(region)
        db_session.commit()

        repo = MultiplierRepository(db_session)
        assert repo.get_region_multiplier(region.id) == 2.5
        assert repo.get_region_multiplier(9999) == 1.0

    def test_get_all_regions(self, db_session):
        from app.persistence.models import RegionMultiplier
        db_session.add(RegionMultiplier(region_name="India", multiplier=1.0))
        db_session.add(RegionMultiplier(region_name="US", multiplier=2.5))
        db_session.commit()

        repo = MultiplierRepository(db_session)
        assert len(repo.get_all_regions()) == 2
