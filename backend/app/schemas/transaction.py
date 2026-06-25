"""Transaction request/response schemas."""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""

    user_id: int = Field(..., gt=0, description="User ID")
    amount: float = Field(..., gt=0, le=1_000_000, description="Transaction amount")
    idempotency_key: str = Field(..., min_length=1, max_length=255, description="Unique request identifier")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 1_000_000:
            raise ValueError("Amount exceeds maximum limit")
        return round(v, 2)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "amount": 100.50,
                "idempotency_key": "txn_unique_key_12345",
            }
        }


class TransactionResponse(BaseModel):
    """Schema for transaction response."""

    id: int
    user_id: int
    amount: float
    points: float
    idempotency_key: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "amount": 100.50,
                "points": 150.75,
                "idempotency_key": "txn_unique_key_12345",
                "created_at": "2024-01-15T10:30:00Z",
            }
        }


class TransactionSummaryResponse(BaseModel):
    """Schema for transaction creation response with user summary."""

    transaction_id: int
    points_earned: float
    updated_total_points: float
    total_transactions: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": 1,
                "points_earned": 150.75,
                "updated_total_points": 150.75,
                "total_transactions": 1,
                "message": "Transaction processed successfully",
            }
        }
