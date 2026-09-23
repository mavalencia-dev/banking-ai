from decimal import Decimal

from app.application.transfer_service import TransferService
from app.infrastructure.database import SessionLocal


def main():

    db = SessionLocal()

    try:
        service = TransferService(db)

        result = service.transfer(
            source_account_id=1,
            beneficiary_id=1,
            amount=Decimal("5000.00"),
            idempotency_key="TEST-TRANSFER-001",
            reference="TRF-TEST-001",
        )

        print("\nTransfer result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()