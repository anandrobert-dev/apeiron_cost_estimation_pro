"""
Apeiron CostEstimation Pro – Audit Repository
==============================================
All database operations for AuditLog entity.
"""

from app.persistence.repositories.base_repository import BaseRepository
from app.persistence.models import AuditLog


class AuditRepository(BaseRepository):
    """Repository for audit log operations."""

    def log(
        self,
        table_name: str,
        record_id: int,
        action: str,
        field_name: str = "",
        old_value: str = "",
        new_value: str = "",
    ) -> AuditLog:
        """Write an audit log entry."""
        entry = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            field_name=field_name,
            old_value=str(old_value),
            new_value=str(new_value),
        )
        self.session.add(entry)
        self.session.commit()
        return entry

    def get_for_record(self, table_name: str, record_id: int) -> list[AuditLog]:
        """Get all audit entries for a specific record."""
        return (
            self.session.query(AuditLog)
            .filter_by(table_name=table_name, record_id=record_id)
            .order_by(AuditLog.timestamp.desc())
            .all()
        )

    def get_recent(self, limit: int = 50) -> list[AuditLog]:
        """Get most recent audit entries."""
        return (
            self.session.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
