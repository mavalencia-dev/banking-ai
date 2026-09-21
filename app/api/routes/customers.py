from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.schemas.account import AccountResponse
from app.api.schemas.customer import CustomerResponse
from app.application.account_service import AccountService
from app.application.customer_service import CustomerService
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from app.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)

router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"],
)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    service = CustomerService(
        CustomerRepository(db)
    )

    customer = service.get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.get(
    "/{customer_id}/accounts",
    response_model=list[AccountResponse],
)
def get_customer_accounts(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer_service = CustomerService(
        CustomerRepository(db)
    )

    customer = customer_service.get_customer(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    account_service = AccountService(
        AccountRepository(db)
    )

    return account_service.get_customer_accounts(customer_id)