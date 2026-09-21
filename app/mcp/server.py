from mcp.server.fastmcp import FastMCP

from app.application.account_service import AccountService
from app.application.customer_service import CustomerService
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from app.infrastructure.repositories.customer_repository import (
    CustomerRepository,
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


if __name__ == "__main__":
    mcp.run()