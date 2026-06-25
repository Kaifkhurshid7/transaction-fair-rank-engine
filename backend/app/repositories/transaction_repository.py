"""Transaction repository for data access."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.transaction import Transaction, Idempotency
from app.core.exceptions import DuplicateRequestException, ResourceNotFound
import hashlib
import json


class TransactionRepository:
    """Repository for transaction data operations."""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        amount: float,
        points: float,
        idempotency_key: str,
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            points=points,
            idempotency_key=idempotency_key,
        )
        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def get_by_id(db: Session, transaction_id: int) -> Transaction:
        """Get transaction by ID."""
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ResourceNotFound("Transaction", transaction_id)
        return transaction

    @staticmethod
    def get_by_idempotency_key(db: Session, key: str) -> Optional[Transaction]:
        """Get transaction by idempotency key."""
        return db.query(Transaction).filter(Transaction.idempotency_key == key).first()

    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: int,
        limit: int = 100,
    ) -> List[Transaction]:
        """Get transactions for a user."""
        return (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_recent_transactions(
        db: Session,
        user_id: int,
        seconds: int = 60,
    ) -> int:
        """Count transactions for user in recent time window."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=seconds)
        return (
            db.query(func.count(Transaction.id))
            .filter(
                Transaction.user_id == user_id,
                Transaction.created_at >= cutoff_time,
            )
            .scalar()
        )

    @staticmethod
    def get_or_create_idempotency(
        db: Session,
        key: str,
        request_hash: str,
        response_payload: str,
    ) -> tuple[Idempotency, bool]:
        """Get existing idempotency record or create new one."""
        existing = db.query(Idempotency).filter(Idempotency.key == key).first()
        
        if existing:
            # Verify request hash matches (optional safety check)
            return existing, False
        
        idempotency = Idempotency(
            key=key,
            request_hash=request_hash,
            response_payload=response_payload,
        )
        db.add(idempotency)
        db.flush()
        return idempotency, True

    @staticmethod
    def cleanup_old_idempotency_records(db: Session, days: int = 7) -> int:
        """Delete old idempotency records."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(Idempotency).filter(
            Idempotency.created_at < cutoff_time
        ).delete()
        db.flush()
        return deleted


class TransactionService:
    """Service layer for transaction operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TransactionRepository()

    def create_transaction(
        self,
        user_id: int,
        amount: float,
        points: float,
        idempotency_key: str,
    ) -> Transaction:
        """Create transaction with idempotency."""
        # Check for duplicate
        existing = self.repo.get_by_idempotency_key(self.db, idempotency_key)
        if existing:
            raise DuplicateRequestException(idempotency_key)
        
        # Create new transaction
        return self.repo.create(
            self.db,
            user_id=user_id,
            amount=amount,
            points=points,
            idempotency_key=idempotency_key,
        )
