"""
Apeiron CostEstimation Pro – Database Setup
============================================
SQLite initialization, session management, and seed data.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base, RegionMultiplier
)

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
    Seed default region multipliers.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
    _seed_defaults(engine)
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
