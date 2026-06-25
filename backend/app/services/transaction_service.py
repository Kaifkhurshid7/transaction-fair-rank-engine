"""Transaction business logic service."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib
import json

from app.models.transaction import Transaction, Idempotency
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.utils.scoring import calculate_points, detect_suspicious_activity
from app.utils.validators import validate_amount, validate_idempotency_key
from app.core.exceptions import (
    ValidationException,
    DuplicateRequestException,
    AbuseDetectedException,
    ResourceNotFound,
)
from app.core.config import settings


class TransactionService:
    """Service for managing transaction operations."""

    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository()
        self.user_repo = UserRepository()

    def create_transaction(
        self,
        user_id: int,
        amount: float,
        idempotency_key: str,
    ) -> tuple[Transaction, dict]:
        """
        Create a new transaction with comprehensive validation and safeguards.
        
        Implements:
        - Input validation
        - Duplicate detection via idempotency key
        - Abuse prevention (rate limiting, suspicious activity)
        - Atomic database operations with locking
        - Points calculation
        
        Returns:
            (transaction, response_dict)
        """
        # Validate inputs
        amount = validate_amount(amount)
        idempotency_key = validate_idempotency_key(idempotency_key)

        # Check for existing transaction (duplicate prevention)
        existing_txn = self.transaction_repo.get_by_idempotency_key(self.db, idempotency_key)
        if existing_txn:
            raise DuplicateRequestException(idempotency_key)

        # Verify user exists and lock for update
        user = self.user_repo.get_by_id(self.db, user_id)

        # Detect suspicious activity
        recent_count = self.transaction_repo.count_recent_transactions(
            self.db,
            user_id,
            seconds=60,
        )
        is_suspicious, reason = detect_suspicious_activity(amount, recent_count + 1)
        if is_suspicious:
            raise AbuseDetectedException(reason)

        # Calculate points
        points = calculate_points(amount)

        # Create transaction within atomic operation
        try:
            transaction = self.transaction_repo.create(
                self.db,
                user_id=user_id,
                amount=amount,
                points=points,
                idempotency_key=idempotency_key,
            )

            # Update user totals atomically with row locking
            self.user_repo.update_totals(
                self.db,
                user_id=user_id,
                amount_delta=amount,
                points_delta=points,
            )

            # Check if this is first transaction on a new day
            last_transaction = (
                self.db.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.id != transaction.id,
                )
                .order_by(Transaction.created_at.desc())
                .first()
            )

            if last_transaction:
                # Check if more than 1 day has passed
                if (datetime.utcnow() - last_transaction.created_at).days > 0:
                    self.user_repo.increment_active_days(self.db, user_id)

            # Commit transaction
            self.db.commit()

            # Refresh user to get updated values
            self.db.refresh(user)

            response = {
                "transaction_id": transaction.id,
                "points_earned": points,
                "updated_total_points": user.total_points,
                "total_transactions": user.transaction_count,
                "message": "Transaction processed successfully",
            }

            return transaction, response

        except Exception as e:
            self.db.rollback()
            raise

    def get_transaction(self, transaction_id: int) -> Transaction:
        """Get transaction by ID."""
        return self.transaction_repo.get_by_id(self.db, transaction_id)

    def get_user_transactions(
        self,
        user_id: int,
        limit: int = 100,
    ) -> list[Transaction]:
        """Get recent transactions for user."""
        return self.transaction_repo.get_user_transactions(self.db, user_id, limit)
