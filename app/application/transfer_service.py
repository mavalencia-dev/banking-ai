from datetime import datetime
from decimal import Decimal
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.models import (
    Account,
    Beneficiary,
    Transaction,
    Transfer,
)


class TransferService:

    def __init__(self, db: Session):
        self.db = db

    def confirm_transfer(
        self,
        transfer_id: int,
    ) -> dict:

        transfer = self.db.scalar(
            select(Transfer)
            .where(Transfer.id == transfer_id)
            .with_for_update()
        )

        if transfer is None:
            return {
                "success": False,
                "error": "Transfer not found",
            }

        if transfer.status == "COMPLETED":
            return {
                "success": True,
                "already_completed": True,
                "transfer_id": transfer.id,
                "reference": transfer.reference,
                "status": transfer.status,
                "amount": str(transfer.amount),
                "currency": transfer.currency,
            }

        if transfer.status != "PENDING_CONFIRMATION":
            return {
                "success": False,
                "error": (
                    f"Transfer cannot be confirmed "
                    f"from status {transfer.status}"
                ),
            }

        source_account = self.db.scalar(
            select(Account)
            .where(Account.id == transfer.source_account_id)
            .with_for_update()
        )

        destination_account = self.db.scalar(
            select(Account)
            .where(Account.id == transfer.destination_account_id)
            .with_for_update()
        )

        if source_account is None:
            return {
                "success": False,
                "error": "Source account not found",
            }

        if destination_account is None:
            return {
                "success": False,
                "error": "Destination account not found",
            }

        if source_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Source account is not active",
            }

        if destination_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Destination account is not active",
            }

        if source_account.balance < transfer.amount:
            return {
                "success": False,
                "error": "Insufficient funds",
            }

        amount = transfer.amount
        now = datetime.utcnow()

        source_account.balance -= amount
        destination_account.balance += amount

        debit_transaction = Transaction(
            account_id=source_account.id,
            transaction_type="DEBIT",
            amount=amount,
            currency=transfer.currency,
            description="Transfer",
            reference=f"{transfer.reference}-DEBIT",
            status="COMPLETED",
            created_at=now,
        )

        credit_transaction = Transaction(
            account_id=destination_account.id,
            transaction_type="CREDIT",
            amount=amount,
            currency=transfer.currency,
            description="Transfer",
            reference=f"{transfer.reference}-CREDIT",
            status="COMPLETED",
            created_at=now,
        )

        transfer.status = "COMPLETED"
        transfer.completed_at = now

        self.db.add(debit_transaction)
        self.db.add(credit_transaction)

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return {
            "success": True,
            "already_completed": False,
            "transfer_id": transfer.id,
            "reference": transfer.reference,
            "status": transfer.status,
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "amount": str(amount),
            "currency": transfer.currency,
        }

    def prepare_transfer(
        self,
        source_account_id: int,
        beneficiary_id: int,
        amount: Decimal,
        idempotency_key: str,
    ) -> dict:

        if amount <= Decimal("0"):
            return {
                "success": False,
                "error": "Transfer amount must be greater than zero",
            }

        existing_transfer = self.db.scalar(
            select(Transfer).where(
                Transfer.idempotency_key == idempotency_key
            )
        )

        if existing_transfer:
            return {
                "success": True,
                "existing": True,
                "transfer_id": existing_transfer.id,
                "reference": existing_transfer.reference,
                "status": existing_transfer.status,
                "amount": str(existing_transfer.amount),
                "currency": existing_transfer.currency,
            }

        source_account = self.db.scalar(
            select(Account).where(
                Account.id == source_account_id
            )
        )

        if source_account is None:
            return {
                "success": False,
                "error": "Source account not found",
            }

        if source_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Source account is not active",
            }

        beneficiary = self.db.scalar(
            select(Beneficiary).where(
                Beneficiary.id == beneficiary_id
            )
        )

        if beneficiary is None:
            return {
                "success": False,
                "error": "Beneficiary not found",
            }

        if beneficiary.status != "ACTIVE":
            return {
                "success": False,
                "error": "Beneficiary is not active",
            }

        if beneficiary.customer_id != source_account.customer_id:
            return {
                "success": False,
                "error": "Beneficiary does not belong to account owner",
            }

        destination_account = self.db.scalar(
            select(Account).where(
                Account.account_number
                == beneficiary.account_number
            )
        )

        if destination_account is None:
            return {
                "success": False,
                "error": "Destination account not found",
            }

        if destination_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Destination account is not active",
            }

        if source_account.currency != destination_account.currency:
            return {
                "success": False,
                "error": "Currency mismatch",
            }

        if source_account.balance < amount:
            return {
                "success": False,
                "error": "Insufficient funds",
            }

        reference = (
            f"TRF-{datetime.utcnow():%Y%m%d%H%M%S}"
            f"-{secrets.token_hex(4).upper()}"
        )

        transfer = Transfer(
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            amount=amount,
            currency=source_account.currency,
            status="PENDING_CONFIRMATION",
            reference=reference,
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow(),
        )

        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)

        return {
            "success": True,
            "existing": False,
            "confirmation_required": True,
            "transfer_id": transfer.id,
            "reference": transfer.reference,
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "beneficiary_name": beneficiary.name,
            "beneficiary_bank": beneficiary.bank_name,
            "amount": str(amount),
            "currency": source_account.currency,
            "status": transfer.status,
        }

    def transfer(
        self,
        source_account_id: int,
        beneficiary_id: int,
        amount: Decimal,
        idempotency_key: str,
        reference: str,
    ) -> dict:

        # -----------------------------------------
        # 1. Validate amount
        # -----------------------------------------

        if amount <= Decimal("0"):
            return {
                "success": False,
                "error": "Transfer amount must be greater than zero",
            }

        # -----------------------------------------
        # 2. Check idempotency
        # -----------------------------------------

        existing_transfer = self.db.scalar(
            select(Transfer).where(
                Transfer.idempotency_key == idempotency_key
            )
        )

        if existing_transfer:
            return {
                "success": True,
                "duplicate": True,
                "transfer_id": existing_transfer.id,
                "reference": existing_transfer.reference,
                "status": existing_transfer.status,
                "amount": str(existing_transfer.amount),
                "currency": existing_transfer.currency,
            }

        # -----------------------------------------
        # 3. Find source account
        # -----------------------------------------

        source_account = self.db.scalar(
            select(Account)
            .where(Account.id == source_account_id)
            .with_for_update()
        )

        if source_account is None:
            return {
                "success": False,
                "error": "Source account not found",
            }

        # -----------------------------------------
        # 4. Validate source account
        # -----------------------------------------

        if source_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Source account is not active",
            }

        # -----------------------------------------
        # 5. Find beneficiary
        # -----------------------------------------

        beneficiary = self.db.scalar(
            select(Beneficiary)
            .where(Beneficiary.id == beneficiary_id)
        )

        if beneficiary is None:
            return {
                "success": False,
                "error": "Beneficiary not found",
            }

        # -----------------------------------------
        # 6. Validate beneficiary
        # -----------------------------------------

        if beneficiary.status != "ACTIVE":
            return {
                "success": False,
                "error": "Beneficiary is not active",
            }

        if beneficiary.customer_id != source_account.customer_id:
            return {
                "success": False,
                "error": "Beneficiary does not belong to account owner",
            }

        # -----------------------------------------
        # 7. Find destination account
        # -----------------------------------------

        destination_account = self.db.scalar(
            select(Account)
            .where(
                Account.account_number
                == beneficiary.account_number
            )
            .with_for_update()
        )

        if destination_account is None:
            return {
                "success": False,
                "error": "Destination account not found",
            }

        # -----------------------------------------
        # 8. Validate destination account
        # -----------------------------------------

        if destination_account.status != "ACTIVE":
            return {
                "success": False,
                "error": "Destination account is not active",
            }

        # -----------------------------------------
        # 9. Validate currency
        # -----------------------------------------

        if source_account.currency != destination_account.currency:
            return {
                "success": False,
                "error": "Currency mismatch",
            }

        if source_account.currency != "PHP":
            return {
                "success": False,
                "error": "Only PHP transfers are supported",
            }

        # -----------------------------------------
        # 10. Validate balance
        # -----------------------------------------

        if source_account.balance < amount:
            return {
                "success": False,
                "error": "Insufficient funds",
            }

        # -----------------------------------------
        # 11. Perform transfer
        # -----------------------------------------

        source_account.balance -= amount
        destination_account.balance += amount

        now = datetime.utcnow()

        # -----------------------------------------
        # 12. Create debit transaction
        # -----------------------------------------

        debit_transaction = Transaction(
            account_id=source_account.id,
            transaction_type="DEBIT",
            amount=amount,
            currency=source_account.currency,
            description="Transfer",
            reference=f"{reference}-DEBIT",
            status="COMPLETED",
            created_at=now,
        )

        # -----------------------------------------
        # 13. Create credit transaction
        # -----------------------------------------

        credit_transaction = Transaction(
            account_id=destination_account.id,
            transaction_type="CREDIT",
            amount=amount,
            currency=destination_account.currency,
            description="Transfer",
            reference=f"{reference}-CREDIT",
            status="COMPLETED",
            created_at=now,
        )

        # -----------------------------------------
        # 14. Create transfer record
        # -----------------------------------------

        transfer = Transfer(
            source_account_id=source_account.id,
            destination_account_id=destination_account.id,
            amount=amount,
            currency=source_account.currency,
            status="COMPLETED",
            reference=reference,
            idempotency_key=idempotency_key,
            created_at=now,
            completed_at=now,
        )

        self.db.add(debit_transaction)
        self.db.add(credit_transaction)
        self.db.add(transfer)

        # -----------------------------------------
        # 15. Commit atomically
        # -----------------------------------------

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return {
            "success": True,
            "duplicate": False,
            "transfer_id": transfer.id,
            "reference": transfer.reference,
            "status": transfer.status,
            "source_account_id": source_account.id,
            "destination_account_id": destination_account.id,
            "amount": str(amount),
            "currency": source_account.currency,
        }