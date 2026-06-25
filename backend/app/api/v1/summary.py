"""User summary API endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.summary import UserSummaryResponse
from app.services.summary_service import SummaryService
from app.repositories.user_repository import UserRepository
from app.core.logging import get_logger
from app.core.exceptions import ResourceNotFound

logger = get_logger(__name__)
router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get(
    "/{user_id}",
    response_model=UserSummaryResponse,
    summary="Get user summary",
    responses={
        200: {"description": "Summary retrieved successfully"},
        404: {"description": "User not found"},
    },
)
async def get_user_summary(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserSummaryResponse:
    """
    Get comprehensive summary for a user.
    
    Returns:
    - User profile information
    - Transaction statistics (total amount, count)
    - Earned points
    - Consistency score (0-1)
    - Current ranking and score
    - Timestamps
    
    **Parameters:**
    - `user_id`: User ID to retrieve summary for
    
    **Returns:**
    Complete user profile with ranking information
    """
    logger.info(f"Retrieving summary for user {user_id}")

    try:
        service = SummaryService(db)
        summary = service.get_user_summary(user_id)
        return UserSummaryResponse(**summary)
    except ResourceNotFound:
        logger.warning(f"User not found: {user_id}")
        raise


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    responses={
        201: {"description": "User created"},
        400: {"description": "Invalid input"},
    },
)
async def create_user(
    name: str,
    email: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    Create a new user in the system.
    
    Users must have a unique email address.
    
    **Parameters:**
    - `name`: User's display name
    - `email`: User's email address (must be unique)
    
    **Returns:**
    - User ID
    - User details
    """
    logger.info(f"Creating user: {email}")

    user_repo = UserRepository()
    
    # Check if user already exists
    existing_user = user_repo.get_by_email(db, email)
    if existing_user:
        return {
            "user_id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "message": "User already exists",
        }

    # Create new user
    user = user_repo.create(db, name=name, email=email)
    db.commit()

    logger.info(f"User created: {user.id}")

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "message": "User created successfully",
    }
