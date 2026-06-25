"""Ranking request/response schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import List


class RankingEntry(BaseModel):
    """Schema for a single ranking entry."""

    rank: int
    user_id: int
    name: str
    email: str
    total_points: float
    total_amount: float
    transaction_count: int
    consistency_score: float
    score: float
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "rank": 1,
                "user_id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "total_points": 5000.0,
                "total_amount": 10000.0,
                "transaction_count": 50,
                "consistency_score": 0.85,
                "score": 5234.5,
                "created_at": "2024-01-15T10:30:00Z",
            }
        }


class RankingResponse(BaseModel):
    """Schema for ranking response."""

    total_users: int
    rankings: List[RankingEntry]

    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 100,
                "rankings": [
                    {
                        "rank": 1,
                        "user_id": 1,
                        "name": "John Doe",
                        "email": "john@example.com",
                        "total_points": 5000.0,
                        "total_amount": 10000.0,
                        "transaction_count": 50,
                        "consistency_score": 0.85,
                        "score": 5234.5,
                        "created_at": "2024-01-15T10:30:00Z",
                    }
                ],
            }
        }
