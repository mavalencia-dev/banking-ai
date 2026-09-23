from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import Transfer


class TransferRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Transfer | None:

        statement = (
            select(Transfer)
            .where(
                Transfer.idempotency_key == idempotency_key
            )
        )

        return self.db.scalar(statement)

    def find_by_reference(
        self,
        reference: str,
    ) -> Transfer | None:

        statement = (
            select(Transfer)
            .where(
                Transfer.reference == reference
            )
        )

        return self.db.scalar(statement)