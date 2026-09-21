from app.infrastructure.models import Account, Transaction
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)


class AccountService:

    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def get_account(self, account_id: int) -> Account | None:
        return self.repository.find_by_id(account_id)

    def get_customer_accounts(
        self,
        customer_id: int,
    ) -> list[Account]:
        return self.repository.find_by_customer_id(customer_id)

    def get_transactions(
        self,
        account_id: int,
    ) -> list[Transaction]:
        return self.repository.find_transactions(account_id)