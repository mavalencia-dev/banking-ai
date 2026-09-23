from app.application.transfer_service import TransferService
from app.infrastructure.database import SessionLocal


def main():

    db = SessionLocal()

    try:
        service = TransferService(db)

        result = service.confirm_transfer(
            transfer_id=1,
        )

        print("\nConfirm transfer result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()