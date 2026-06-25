"""User summary business logic service."""
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.ranking_service import RankingService
from app.utils.scoring import calculate_consistency_score
from app.core.exceptions import ResourceNotFound


class SummaryService:
    """Service for generating user summaries."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()
        self.ranking_service = RankingService(db)

    def get_user_summary(self, user_id: int) -> dict:
        """
        Get comprehensive summary for a user.
        
        Includes:
        - User details
        - Transaction statistics
        - Ranking information
        - Consistency metrics
        """
        user = self.user_repo.get_by_id(self.db, user_id)

        # Calculate consistency score
        consistency = calculate_consistency_score(user.created_at, user.active_days)

        # Get ranking
        try:
            rank, ranking_entry = self.ranking_service.get_user_rank(user_id)
            ranking_score = ranking_entry["score"]
        except ResourceNotFound:
            rank = 0
            ranking_score = 0.0

        summary = {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "total_amount": user.total_amount,
            "total_points": user.total_points,
            "transaction_count": user.transaction_count,
            "consistency_score": consistency,
            "current_rank": rank,
            "ranking_score": ranking_score,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return summary
