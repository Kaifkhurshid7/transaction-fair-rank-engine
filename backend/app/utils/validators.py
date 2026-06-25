"""Validation utilities."""
from app.core.exceptions import ValidationException
from app.core.config import settings
import re


def validate_amount(amount: float) -> float:
    """Validate transaction amount."""
    if amount <= 0:
        raise ValidationException("Amount must be greater than 0")
    
    if amount > settings.MAX_TRANSACTION_AMOUNT:
        raise ValidationException(
            f"Amount exceeds maximum limit of ${settings.MAX_TRANSACTION_AMOUNT:,.2f}"
        )
    
    return round(amount, 2)


def validate_idempotency_key(key: str) -> str:
    """Validate idempotency key format."""
    if not key or len(key) > 255:
        raise ValidationException("Idempotency key must be between 1 and 255 characters")
    
    # Allow alphanumeric, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9\-_]+$", key):
        raise ValidationException("Idempotency key contains invalid characters")
    
    return key


def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationException("Invalid email format")
    return email


def validate_name(name: str) -> str:
    """Validate user name."""
    if not name or len(name) > 255:
        raise ValidationException("Name must be between 1 and 255 characters")
    
    return name.strip()
