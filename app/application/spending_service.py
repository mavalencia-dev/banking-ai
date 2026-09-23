from datetime import datetime
from decimal import Decimal

from app.infrastructure.models import Transaction
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)

from collections import defaultdict

class SpendingService:

    def __init__(
        self,
        repository: AccountRepository,
    ):
        self.repository = repository

    def get_spending_summary(
        self,
        account_id: int,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:

        account = self.repository.find_by_id(
            account_id
        )

        if account is None:
            return {
                "success": False,
                "error": "Account not found",
            }

        if start_date and end_date:
            transactions = (
                self.repository.find_transactions_between(
                    account_id,
                    start_date,
                    end_date,
                )
            )
        else:
            transactions = self.repository.find_transactions(
                account_id
            )

        spending = []

        for transaction in transactions:

            if transaction.transaction_type != "DEBIT":
                continue

            if start_date and transaction.created_at < start_date:
                continue

            if end_date and transaction.created_at >= end_date:
                continue

            if category:
                if transaction.description.lower() != category.lower():
                    continue

            spending.append(transaction)

        total = sum(
            (
                transaction.amount
                for transaction in spending
            ),
            Decimal("0"),
        )

        return {
            "success": True,
            "account_id": account.id,
            "account_number": account.account_number,
            "currency": account.currency,
            "category": category,
            "transaction_count": len(spending),
            "total_spending": str(total),
            "transactions": [
                {
                    "reference": transaction.reference,
                    "amount": str(transaction.amount),
                    "description": transaction.description,
                    "created_at": (
                        transaction.created_at.isoformat()
                    ),
                }
                for transaction in spending
            ],
        }

    def get_spending_by_category(
        self,
        account_id: int,
    ) -> dict:

        account = self.repository.find_by_id(
            account_id
        )

        if account is None:
            return {
                "success": False,
                "error": "Account not found",
            }

        transactions = self.repository.find_transactions(
            account_id
        )

        totals = defaultdict(Decimal)

        for transaction in transactions:

            if transaction.transaction_type != "DEBIT":
                continue

            category = transaction.description

            totals[category] += transaction.amount

        return {
            "success": True,
            "account_id": account.id,
            "currency": account.currency,
            "categories": {
                category: str(amount)
                for category, amount in totals.items()
            },
        }