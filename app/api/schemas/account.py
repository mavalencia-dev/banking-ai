from decimal import Decimal

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: int
    customer_id: int
    account_number: str
    account_type: str
    currency: str
    balance: Decimal
    status: str


class AccountBalanceResponse(BaseModel):
    account_id: int
    account_number: str
    currency: str
    balance: Decimal