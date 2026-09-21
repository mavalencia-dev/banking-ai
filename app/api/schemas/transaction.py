from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    currency: str
    description: str
    reference: str
    status: str
    created_at: datetime