from decimal import Decimal
from datetime import datetime, timedelta

from app.infrastructure.database import SessionLocal
from app.infrastructure.models import (
    Account,
    Base,
    Customer,
    Transaction,
    Beneficiary,
)


def main():
    db = SessionLocal()

    try:
        existing_customer = db.query(Customer).first()

        if existing_customer:
            print("Database already contains data.")
            return

        michael = Customer(
            name="Michael Valencia",
            email="michael@example.com",
            status="ACTIVE",
        )

        juan = Customer(
            name="Juan Santos",
            email="juan@example.com",
            status="ACTIVE",
        )

        db.add_all([michael, juan])
        db.flush()

        checking = Account(
            customer_id=michael.id,
            account_number="1000000001",
            account_type="CHECKING",
            currency="PHP",
            balance=Decimal("125000.00"),
            status="ACTIVE",
        )

        savings = Account(
            customer_id=michael.id,
            account_number="1000000002",
            account_type="SAVINGS",
            currency="PHP",
            balance=Decimal("250000.00"),
            status="ACTIVE",
        )

        juan_account = Account(
            customer_id=juan.id,
            account_number="2000000001",
            account_type="SAVINGS",
            currency="PHP",
            balance=Decimal("50000.00"),
            status="ACTIVE",
        )

        db.add_all([
            checking,
            savings,
            juan_account,
        ])

        db.flush()

        beneficiary = Beneficiary(
            customer_id=michael.id,
            name="Juan Santos",
            bank_name="Demo Bank",
            account_number="2000000001",
            status="ACTIVE",
        )

        db.add(beneficiary)

        now = datetime.utcnow()

        transactions = [
            Transaction(
                account_id=checking.id,
                transaction_type="CREDIT",
                amount=Decimal("150000.00"),
                currency="PHP",
                description="Salary",
                reference="TXN-100001",
                status="COMPLETED",
                created_at=now - timedelta(days=20),
            ),
            Transaction(
                account_id=checking.id,
                transaction_type="DEBIT",
                amount=Decimal("1200.00"),
                currency="PHP",
                description="Restaurant",
                reference="TXN-100002",
                status="COMPLETED",
                created_at=now - timedelta(days=10),
            ),
            Transaction(
                account_id=checking.id,
                transaction_type="DEBIT",
                amount=Decimal("2500.00"),
                currency="PHP",
                description="Groceries",
                reference="TXN-100003",
                status="COMPLETED",
                created_at=now - timedelta(days=7),
            ),
            Transaction(
                account_id=checking.id,
                transaction_type="DEBIT",
                amount=Decimal("800.00"),
                currency="PHP",
                description="Restaurant",
                reference="TXN-100004",
                status="COMPLETED",
                created_at=now - timedelta(days=3),
            ),
        ]

        db.add_all(transactions)

        db.commit()

        print("Banking demo data created successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()