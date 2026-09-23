from mcp.server.fastmcp import FastMCP
from datetime import datetime

from app.application.account_service import AccountService
from app.application.customer_service import CustomerService
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from app.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)

from app.application.spending_service import (
    SpendingService,
)

mcp = FastMCP("Banking MCP Server")


@mcp.tool()
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


@mcp.tool()
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

@mcp.tool()
def get_spending_summary(
    account_id: int,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """
    Calculate deterministic spending for an account.

    Dates must be ISO-8601 strings.
    """

    db = SessionLocal()

    try:
        repository = AccountRepository(db)

        service = SpendingService(
            repository
        )

        parsed_start = (
            datetime.fromisoformat(start_date)
            if start_date
            else None
        )

        parsed_end = (
            datetime.fromisoformat(end_date)
            if end_date
            else None
        )

        return service.get_spending_summary(
            account_id=account_id,
            category=category,
            start_date=parsed_start,
            end_date=parsed_end,
        )

    finally:
        db.close()


@mcp.tool()
def get_customer(customer_id: int) -> dict:
    """
    Get customer information.
    """

    db = SessionLocal()

    try:
        repository = CustomerRepository(db)
        service = CustomerService(repository)

        customer = service.get_customer(customer_id)

        if customer is None:
            return {
                "success": False,
                "error": "Customer not found",
            }

        return {
            "success": True,
            "customer_id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "status": customer.status,
        }

    finally:
        db.close()

@mcp.tool()
def get_spending_by_category(
    account_id: int,
) -> dict:
    """
    Calculate spending grouped by category.
    """

    db = SessionLocal()

    try:

        repository = AccountRepository(db)

        service = SpendingService(
            repository
        )

        return service.get_spending_by_category(
            account_id
        )

    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()