from decimal import Decimal

from app.application.account_service import AccountService
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from app.infrastructure.database import SessionLocal


def get_account_balance(account_id: int) -> dict:
    """
    Get the current balance of a banking account.
    """

    db = SessionLocal()

    try:
        repository = AccountRepository(db)
        service = AccountService(repository)

        account = service.get_account(account_id)

        if account is None:
            return {
                "success": False,
                "error": "Account not found",
            }

        return {
            "success": True,
            "account_id": account.id,
            "account_number": account.account_number,
            "currency": account.currency,
            "balance": str(account.balance),
        }

    finally:
        db.close()

def get_account_transactions(account_id: int) -> dict:
    """
    Get transactions for a banking account.
    """

    db = SessionLocal()

    try:
        repository = AccountRepository(db)
        service = AccountService(repository)

        account = service.get_account(account_id)

        if account is None:
            return {
                "success": False,
                "error": "Account not found",
            }

        transactions = service.get_transactions(account_id)

        return {
            "success": True,
            "account_id": account.id,
            "account_number": account.account_number,
            "transactions": [
                {
                    "id": transaction.id,
                    "type": transaction.transaction_type,
                    "amount": str(transaction.amount),
                    "currency": transaction.currency,
                    "description": transaction.description,
                    "reference": transaction.reference,
                    "status": transaction.status,
                    "created_at": transaction.created_at.isoformat(),
                }
                for transaction in transactions
            ],
        }

    finally:
        db.close()