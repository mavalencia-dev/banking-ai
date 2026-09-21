from app.infrastructure.models import Customer
from app.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerService:

    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.repository.find_by_id(customer_id)