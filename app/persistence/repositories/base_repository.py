"""
Apeiron CostEstimation Pro – Base Repository
=============================================
Abstract base for all repositories. Provides common session management.
"""


class BaseRepository:
    """Common base for all repository classes."""

    def __init__(self, session):
        self.session = session

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def flush(self):
        """Flush pending changes to the database."""
        self.session.flush()
