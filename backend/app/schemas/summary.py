"""User summary request/response schemas."""
from pydantic import BaseModel, Field
from datetime import datetime


class UserSummaryResponse(BaseModel):
    """Schema for user summary response."""

    user_id: int
    name: str
    email: str
    total_amount: float
    total_points: float
    transaction_count: int
    consistency_score: float
    current_rank: int
    ranking_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "total_amount": 10000.0,
                "total_points": 5000.0,
                "transaction_count": 50,
                "consistency_score": 0.85,
                "current_rank": 1,
                "ranking_score": 5234.5,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T15:45:00Z",
            }
        }
