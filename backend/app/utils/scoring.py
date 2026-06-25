"""Scoring and ranking utilities."""
import math
from datetime import datetime, timedelta
from app.core.config import settings


def calculate_points(amount: float) -> float:
    """
    Calculate points earned from transaction amount.
    
    Formula: points = amount * 1.5
    This incentivizes larger transactions while maintaining fairness.
    """
    return round(amount * 1.5, 2)


def calculate_consistency_score(
    user_created_at: datetime,
    active_days: int,
) -> float:
    """
    Calculate consistency score based on activity over time.
    
    Formula: consistency_score = active_days / days_since_creation
    
    This rewards users who transact regularly over a longer period,
    preventing single large transactions from dominating rankings.
    """
    days_since_creation = (datetime.utcnow() - user_created_at).days + 1
    
    # Minimum 1 day to avoid division by zero
    if days_since_creation < 1:
        days_since_creation = 1
    
    consistency_score = min(active_days / days_since_creation, 1.0)
    return round(consistency_score, 4)


def calculate_ranking_score(
    points: float,
    transaction_count: int,
    consistency_score: float,
) -> float:
    """
    Calculate overall ranking score using weighted formula.
    
    Formula: score = (points * 0.6) + (log(transaction_count + 1) * 20) + (consistency_score * 20)
    
    Breakdown:
    - 60% weight on total points: rewards actual transaction volume
    - 20% weight on activity (logarithmic): encourages regular transactions
      but prevents explosion from high counts
    - 20% weight on consistency: rewards sustained engagement over time
    
    Why this formula is fair:
    1. Logarithmic activity: prevents spamming small transactions
    2. Consistency weight: single whales can't dominate
    3. Points weight: still rewards actual transaction value
    4. Multi-factor: hard to manipulate all three factors simultaneously
    """
    activity_score = math.log(transaction_count + 1) * settings.ACTIVITY_WEIGHT
    consistency_component = consistency_score * settings.CONSISTENCY_WEIGHT
    points_component = points * settings.POINTS_WEIGHT
    
    total_score = points_component + activity_score + consistency_component
    return round(total_score, 2)


def detect_suspicious_activity(
    amount: float,
    transaction_count_in_window: int,
    time_window_seconds: int = 60,
) -> tuple[bool, str]:
    """
    Detect suspicious activity patterns.
    
    Returns:
        (is_suspicious, reason)
    """
    # Check for unusually high amount
    if amount > settings.MAX_TRANSACTION_AMOUNT * 0.8:
        return True, "Transaction amount is unusually high"
    
    # Check for spam transactions
    if transaction_count_in_window > settings.MAX_TRANSACTIONS_PER_MINUTE:
        return (
            True,
            f"Too many transactions in {time_window_seconds}s (limit: {settings.MAX_TRANSACTIONS_PER_MINUTE})",
        )
    
    return False, ""
