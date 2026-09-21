from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import Account, Transaction


class AccountRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, account_id: int) -> Account | None:
        statement = select(Account).where(Account.id == account_id)

        return self.db.scalar(statement)

    def find_by_customer_id(self, customer_id: int) -> list[Account]:
        statement = (
            select(Account)
            .where(Account.customer_id == customer_id)
            .order_by(Account.id)
        )

        return list(self.db.scalars(statement).all())

    def find_transactions(
        self,
        account_id: int,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
        )

        return list(self.db.scalars(statement).all())