"""
Apeiron CostEstimation Pro – Custom Exceptions
===============================================
Application-specific exception classes.
"""


class AppError(Exception):
    """Base exception for all application errors."""
    pass


class ValidationError(AppError):
    """Raised when input validation fails."""
    pass


class NotFoundError(AppError):
    """Raised when a requested entity is not found."""
    pass


class DatabaseError(AppError):
    """Raised when a database operation fails."""
    pass
