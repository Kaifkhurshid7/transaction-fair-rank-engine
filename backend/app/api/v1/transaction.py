"""Transaction API endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionSummaryResponse
from app.services.transaction_service import TransactionService
from app.repositories.user_repository import UserRepository
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post(
    "",
    response_model=TransactionSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
    responses={
        201: {"description": "Transaction created successfully"},
        400: {"description": "Invalid input"},
        404: {"description": "User not found"},
        409: {"description": "Duplicate request"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def create_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionSummaryResponse:
    """
    Create a new transaction for a user.
    
    This endpoint:
    - Validates input (amount, user existence, idempotency key)
    - Prevents duplicate requests using idempotency key
    - Detects suspicious activity
    - Handles concurrent requests safely with database locking
    - Calculates points based on transaction amount
    - Updates user statistics atomically
    
    **Parameters:**
    - `user_id`: User ID (must exist)
    - `amount`: Transaction amount (must be > 0, <= 1,000,000)
    - `idempotency_key`: Unique request identifier for duplicate prevention
    
    **Returns:**
    - Transaction ID
    - Points earned
    - Updated user total points
    - Total transaction count
    """
    logger.info(
        f"Creating transaction for user {request.user_id}",
        extra={"extra": {"user_id": request.user_id, "amount": request.amount}},
    )

    # Create transaction service
    service = TransactionService(db)

    # Create transaction
    transaction, response = service.create_transaction(
        user_id=request.user_id,
        amount=request.amount,
        idempotency_key=request.idempotency_key,
    )

    logger.info(
        f"Transaction created: {transaction.id}",
        extra={"extra": {"transaction_id": transaction.id}},
    )

    return TransactionSummaryResponse(**response)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction details",
)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """
    Get details of a specific transaction.
    
    Returns transaction information including amount, points earned, and timestamp.
    """
    service = TransactionService(db)
    transaction = service.get_transaction(transaction_id)
    return TransactionResponse.from_attributes(transaction)
