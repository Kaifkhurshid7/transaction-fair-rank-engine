"""User repository for data access."""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional

from app.models.user import User
from app.core.exceptions import ResourceNotFound


class UserRepository:
    """Repository for user data operations."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        """Get user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFound("User", user_id)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(
        db: Session,
        name: str,
        email: str,
    ) -> User:
        """Create a new user."""
        user = User(name=name, email=email)
        db.add(user)
        db.flush()
        return user

    @staticmethod
    def get_or_create(
        db: Session,
        name: str,
        email: str,
    ) -> tuple[User, bool]:
        """Get existing user or create new one."""
        user = UserRepository.get_by_email(db, email)
        if user:
            return user, False
        return UserRepository.create(db, name, email), True

    @staticmethod
    def get_all_sorted_by_score(db: Session, limit: int = 100) -> List[User]:
        """Get all users sorted by ranking score."""
        return (
            db.query(User)
            .order_by(desc(User.total_points))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_rank(db: Session, user_id: int) -> Optional[int]:
        """Get user's current rank."""
        # Get the user's total points
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Count how many users have more points
        rank = (
            db.query(func.count(User.id))
            .filter(User.total_points > user.total_points)
            .scalar()
        )
        return (rank or 0) + 1

    @staticmethod
    def update_totals(
        db: Session,
        user_id: int,
        amount_delta: float = 0.0,
        points_delta: float = 0.0,
    ) -> User:
        """Update user totals atomically."""
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise ResourceNotFound("User", user_id)
        
        user.total_amount += amount_delta
        user.total_points += points_delta
        user.transaction_count += 1
        
        db.flush()
        return user

    @staticmethod
    def increment_active_days(db: Session, user_id: int) -> None:
        """Increment active days for a user."""
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if user:
            user.active_days += 1
            db.flush()
