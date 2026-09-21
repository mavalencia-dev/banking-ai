from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.schemas.account import (
    AccountBalanceResponse,
    AccountResponse,
)
from app.api.schemas.transaction import TransactionResponse
from app.application.account_service import AccountService
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)

router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["Accounts"],
)


def get_account_service(
    db: Session = Depends(get_db),
) -> AccountService:
    return AccountService(
        AccountRepository(db)
    )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
)
def get_account(
    account_id: int,
    service: AccountService = Depends(get_account_service),
):
    account = service.get_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return account


@router.get(
    "/{account_id}/balance",
    response_model=AccountBalanceResponse,
)
def get_balance(
    account_id: int,
    service: AccountService = Depends(get_account_service),
):
    account = service.get_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return AccountBalanceResponse(
        account_id=account.id,
        account_number=account.account_number,
        currency=account.currency,
        balance=account.balance,
    )


@router.get(
    "/{account_id}/transactions",
    response_model=list[TransactionResponse],
)
def get_transactions(
    account_id: int,
    service: AccountService = Depends(get_account_service),
):
    account = service.get_account(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return service.get_transactions(account_id)