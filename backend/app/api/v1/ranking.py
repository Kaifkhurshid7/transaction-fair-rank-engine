"""Ranking API endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ranking import RankingResponse, RankingEntry
from app.services.ranking_service import RankingService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get(
    "",
    response_model=RankingResponse,
    summary="Get user rankings",
    responses={
        200: {"description": "Rankings retrieved successfully"},
        400: {"description": "Invalid parameters"},
    },
)
async def get_rankings(
    limit: int = Query(100, ge=1, le=1000, description="Number of rankings to return"),
    db: Session = Depends(get_db),
) -> RankingResponse:
    """
    Get user rankings based on fair scoring algorithm.
    
    The ranking is calculated using a weighted formula:
    ```
    score = (points * 0.6) + (log(transaction_count + 1) * 20) + (consistency_score * 20)
    ```
    
    **Why this formula is fair:**
    1. **Points Weight (60%)**: Rewards actual transaction value
    2. **Activity Weight (20%, logarithmic)**: Encourages regular transactions
       - Uses log() to prevent spamming small transactions
       - log(1) = 0, log(101) ≈ 4.6, so impact diminishes with volume
    3. **Consistency Weight (20%)**: Rewards sustained engagement
       - Formula: active_days / days_since_creation
       - Prevents single large transactions from dominating
       - Single whales can't outrank consistent users
    
    **Abuse Prevention:**
    - Multi-factor scoring makes manipulation hard
    - Can't maximize all three factors simultaneously
    - New users with no history have 0 consistency score
    - High transaction counts alone won't guarantee top ranking
    
    **Parameters:**
    - `limit`: Maximum number of rankings to return (1-1000, default: 100)
    
    **Returns:**
    - Total number of users
    - List of ranking entries (rank, user info, scores)
    """
    logger.info(f"Retrieving rankings with limit {limit}")

    service = RankingService(db)
    total_users, rankings = service.get_rankings(limit=limit)

    ranking_entries = [
        RankingEntry(**ranking) for ranking in rankings
    ]

    return RankingResponse(total_users=total_users, rankings=ranking_entries)


@router.get(
    "/user/{user_id}",
    response_model=RankingEntry,
    summary="Get user ranking",
    responses={
        200: {"description": "User ranking retrieved"},
        404: {"description": "User not found"},
    },
)
async def get_user_ranking(
    user_id: int,
    db: Session = Depends(get_db),
) -> RankingEntry:
    """
    Get specific user's ranking and score.
    
    Returns the user's current rank and calculated score.
    """
    logger.info(f"Retrieving ranking for user {user_id}")

    service = RankingService(db)
    rank, ranking_data = service.get_user_rank(user_id)

    return RankingEntry(**ranking_data)
