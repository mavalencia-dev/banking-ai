from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import Customer


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, customer_id: int) -> Customer | None:
        statement = select(Customer).where(Customer.id == customer_id)

        return self.db.scalar(statement)

    def find_all(self) -> list[Customer]:
        statement = select(Customer).order_by(Customer.id)

        return list(self.db.scalars(statement).all())