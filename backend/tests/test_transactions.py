"""Tests for transaction operations."""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.transaction import Transaction
from app.services.transaction_service import TransactionService
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    ValidationException,
    DuplicateRequestException,
    AbuseDetectedException,
)


@pytest.fixture
def sample_user(db: Session) -> User:
    """Create a sample user for testing."""
    user_repo = UserRepository()
    user = user_repo.create(db, name="Test User", email="test@example.com")
    db.commit()
    return user


def test_create_transaction_success(db: Session, sample_user: User):
    """Test successful transaction creation."""
    service = TransactionService(db)
    
    transaction, response = service.create_transaction(
        user_id=sample_user.id,
        amount=100.0,
        idempotency_key="txn_001",
    )
    
    assert transaction.id is not None
    assert transaction.user_id == sample_user.id
    assert transaction.amount == 100.0
    assert transaction.points == 150.0  # 100 * 1.5
    assert response["points_earned"] == 150.0
    assert response["updated_total_points"] == 150.0


def test_create_transaction_invalid_amount(db: Session, sample_user: User):
    """Test transaction with invalid amount."""
    service = TransactionService(db)
    
    with pytest.raises(ValidationException):
        service.create_transaction(
            user_id=sample_user.id,
            amount=0.0,
            idempotency_key="txn_002",
        )


def test_create_transaction_amount_too_high(db: Session, sample_user: User):
    """Test transaction exceeding maximum amount."""
    service = TransactionService(db)
    
    with pytest.raises(ValidationException):
        service.create_transaction(
            user_id=sample_user.id,
            amount=2_000_000.0,
            idempotency_key="txn_003",
        )


def test_duplicate_transaction_prevention(db: Session, sample_user: User):
    """Test duplicate transaction prevention."""
    service = TransactionService(db)
    
    # First transaction
    service.create_transaction(
        user_id=sample_user.id,
        amount=100.0,
        idempotency_key="txn_dup",
    )
    
    # Attempt duplicate
    with pytest.raises(DuplicateRequestException):
        service.create_transaction(
            user_id=sample_user.id,
            amount=100.0,
            idempotency_key="txn_dup",
        )


def test_multiple_transactions_update_totals(db: Session, sample_user: User):
    """Test that multiple transactions correctly update user totals."""
    service = TransactionService(db)
    
    # Create three transactions
    service.create_transaction(
        user_id=sample_user.id,
        amount=100.0,
        idempotency_key="txn_a",
    )
    service.create_transaction(
        user_id=sample_user.id,
        amount=50.0,
        idempotency_key="txn_b",
    )
    service.create_transaction(
        user_id=sample_user.id,
        amount=25.0,
        idempotency_key="txn_c",
    )
    
    # Verify totals
    user_repo = UserRepository()
    db.refresh(sample_user)
    
    assert sample_user.total_amount == 175.0
    assert sample_user.total_points == 262.5  # (100 + 50 + 25) * 1.5
    assert sample_user.transaction_count == 3


def test_abuse_detection_spam_transactions(db: Session, sample_user: User):
    """Test abuse detection for spam transactions."""
    service = TransactionService(db)
    
    # Create many transactions in quick succession
    for i in range(10):
        service.create_transaction(
            user_id=sample_user.id,
            amount=10.0,
            idempotency_key=f"txn_spam_{i}",
        )
    
    # Next transaction should be flagged
    with pytest.raises(AbuseDetectedException):
        service.create_transaction(
            user_id=sample_user.id,
            amount=10.0,
            idempotency_key="txn_spam_11",
        )
