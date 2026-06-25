"""Tests for ranking calculations."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ranking_service import RankingService
from app.repositories.user_repository import UserRepository
from app.utils.scoring import calculate_ranking_score, calculate_consistency_score


@pytest.fixture
def users_with_data(db: Session):
    """Create multiple users with different activity levels."""
    user_repo = UserRepository()
    
    # User 1: High points, many transactions, consistent
    user1 = user_repo.create(db, "John Doe", "john@example.com")
    user1.total_points = 5000.0
    user1.total_amount = 10000.0
    user1.transaction_count = 100
    user1.active_days = 100
    user1.created_at = datetime.utcnow() - timedelta(days=100)
    
    # User 2: Medium points, few transactions, new
    user2 = user_repo.create(db, "Jane Smith", "jane@example.com")
    user2.total_points = 2000.0
    user2.total_amount = 5000.0
    user2.transaction_count = 20
    user2.active_days = 10
    user2.created_at = datetime.utcnow() - timedelta(days=10)
    
    # User 3: High points, low transactions (whale)
    user3 = user_repo.create(db, "Rich Person", "rich@example.com")
    user3.total_points = 8000.0
    user3.total_amount = 20000.0
    user3.transaction_count = 5
    user3.active_days = 2
    user3.created_at = datetime.utcnow() - timedelta(days=2)
    
    db.commit()
    return [user1, user2, user3]


def test_consistency_score_calculation():
    """Test consistency score calculation."""
    # User with perfect consistency
    created_at = datetime.utcnow() - timedelta(days=100)
    score = calculate_consistency_score(created_at, active_days=100)
    assert score == 1.0
    
    # User with partial consistency
    created_at = datetime.utcnow() - timedelta(days=100)
    score = calculate_consistency_score(created_at, active_days=50)
    assert 0.4 < score < 0.6
    
    # Brand new user
    created_at = datetime.utcnow()
    score = calculate_consistency_score(created_at, active_days=1)
    assert score >= 0.0


def test_ranking_score_calculation():
    """Test ranking score formula."""
    # Test multi-factor scoring
    score = calculate_ranking_score(
        points=5000.0,
        transaction_count=100,
        consistency_score=0.9,
    )
    assert score > 0
    
    # Whale with few transactions should score lower
    whale_score = calculate_ranking_score(
        points=8000.0,
        transaction_count=5,
        consistency_score=0.2,
    )
    
    # Consistent user with moderate points
    consistent_score = calculate_ranking_score(
        points=5000.0,
        transaction_count=100,
        consistency_score=0.9,
    )
    
    # Consistent user should beat whale
    assert consistent_score > whale_score


def test_rankings_ordering(db: Session, users_with_data):
    """Test that rankings are ordered correctly."""
    service = RankingService(db)
    total, rankings = service.get_rankings(limit=100)
    
    assert len(rankings) == 3
    
    # Verify ordering (highest score first)
    for i in range(len(rankings) - 1):
        assert rankings[i]["score"] >= rankings[i + 1]["score"]
    
    # Verify ranks are sequential
    for idx, ranking in enumerate(rankings, 1):
        assert ranking["rank"] == idx


def test_get_user_rank(db: Session, users_with_data):
    """Test retrieving specific user rank."""
    service = RankingService(db)
    user1 = users_with_data[0]
    
    rank, ranking_data = service.get_user_rank(user1.id)
    
    assert rank >= 1
    assert ranking_data["user_id"] == user1.id
    assert ranking_data["rank"] == rank
