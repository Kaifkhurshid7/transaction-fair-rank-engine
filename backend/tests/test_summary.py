"""Tests for user summary functionality."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.summary_service import SummaryService
from app.repositories.user_repository import UserRepository


@pytest.fixture
def user_with_transactions(db: Session):
    """Create a user with transaction data."""
    user_repo = UserRepository()
    user = user_repo.create(db, "Test User", "test@example.com")
    user.total_points = 5000.0
    user.total_amount = 10000.0
    user.transaction_count = 50
    user.active_days = 30
    db.commit()
    return user


def test_get_user_summary(db: Session, user_with_transactions: User):
    """Test retrieving user summary."""
    service = SummaryService(db)
    summary = service.get_user_summary(user_with_transactions.id)
    
    assert summary["user_id"] == user_with_transactions.id
    assert summary["name"] == "Test User"
    assert summary["email"] == "test@example.com"
    assert summary["total_points"] == 5000.0
    assert summary["total_amount"] == 10000.0
    assert summary["transaction_count"] == 50
    assert "consistency_score" in summary
    assert "current_rank" in summary
    assert "ranking_score" in summary


def test_summary_consistency_score(db: Session, user_with_transactions: User):
    """Test consistency score in summary."""
    service = SummaryService(db)
    summary = service.get_user_summary(user_with_transactions.id)
    
    # Consistency score should be between 0 and 1
    assert 0 <= summary["consistency_score"] <= 1.0
