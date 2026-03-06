"""
Apeiron CostEstimation Pro – Test Fixtures
===========================================
Shared pytest fixtures for all test layers.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    """Provide an in-memory SQLite session for persistence tests."""
    from app.persistence.models import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
