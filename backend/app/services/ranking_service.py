"""Ranking business logic service."""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Tuple

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.scoring import calculate_ranking_score, calculate_consistency_score
from app.core.exceptions import ResourceNotFound


class RankingService:
    """Service for calculating and retrieving rankings."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository()

    def calculate_user_score(self, user: User) -> float:
        """Calculate ranking score for a user."""
        consistency = calculate_consistency_score(user.created_at, user.active_days)
        score = calculate_ranking_score(
            user.total_points,
            user.transaction_count,
            consistency,
        )
        return score

    def get_rankings(self, limit: int = 100) -> Tuple[int, List[dict]]:
        """
        Get user rankings sorted by score.
        
        Returns:
            (total_users, [ranking_entries])
        """
        # Get all users
        users = self.db.query(User).all()
        total_users = len(users)

        # Calculate scores for all users
        rankings = []
        for user in users:
            consistency = calculate_consistency_score(user.created_at, user.active_days)
            score = self.calculate_user_score(user)

            rankings.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "total_points": user.total_points,
                "total_amount": user.total_amount,
                "transaction_count": user.transaction_count,
                "consistency_score": consistency,
                "score": score,
                "created_at": user.created_at,
            })

        # Sort by score descending
        rankings.sort(key=lambda x: x["score"], reverse=True)

        # Add rank
        for idx, ranking in enumerate(rankings, 1):
            ranking["rank"] = idx

        # Return top N
        return total_users, rankings[:limit]

    def get_user_rank(self, user_id: int) -> Tuple[int, dict]:
        """
        Get specific user's rank and score.
        
        Returns:
            (rank, ranking_entry)
        """
        total_users, rankings = self.get_rankings(limit=10000)

        for ranking in rankings:
            if ranking["user_id"] == user_id:
                return ranking["rank"], ranking

        raise ResourceNotFound("User", user_id)

    def get_rankings_page(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, int, List[dict]]:
        """
        Get paginated rankings.
        
        Returns:
            (total_users, total_pages, [ranking_entries])
        """
        total_users, all_rankings = self.get_rankings(limit=10000)

        total_pages = (total_users + page_size - 1) // page_size
        
        # Validate page
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return total_users, total_pages, all_rankings[start_idx:end_idx]
