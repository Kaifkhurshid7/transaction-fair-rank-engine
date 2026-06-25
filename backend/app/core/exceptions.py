"""Custom exceptions for the application."""
from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationException(AppException):
    """Raised when validation fails."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ResourceNotFound(AppException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            error_code="NOT_FOUND",
            status_code=404,
        )


class DuplicateRequestException(AppException):
    """Raised when a duplicate request is detected."""

    def __init__(self, idempotency_key: str):
        super().__init__(
            message=f"Duplicate request detected: {idempotency_key}",
            error_code="DUPLICATE_REQUEST",
            status_code=409,
        )


class RateLimitException(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class AbuseDetectedException(AppException):
    """Raised when suspicious activity is detected."""

    def __init__(self, message: str = "Suspicious activity detected"):
        super().__init__(
            message=message,
            error_code="ABUSE_DETECTED",
            status_code=403,
        )


class UnauthorizedException(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
        )
