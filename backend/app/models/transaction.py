"""Transaction model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Transaction(Base):
    """Transaction model for storing individual transactions."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    points = Column(Float, nullable=False)
    
    # Idempotency
    idempotency_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
        CheckConstraint("points > 0", name="ck_transaction_points_positive"),
        Index("ix_transactions_user_id_created_at", "user_id", "created_at"),
        Index("ix_transactions_idempotency_key", "idempotency_key"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, points={self.points})>"


class Idempotency(Base):
    """Idempotency model for storing request idempotency information."""

    __tablename__ = "idempotency"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    request_hash = Column(String(64), nullable=False)
    response_payload = Column(String, nullable=False)  # JSON serialized
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_idempotency_key", "key"),
        Index("ix_idempotency_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Idempotency(key={self.key})>"
