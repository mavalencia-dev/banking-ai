from pprint import pprint

from app.application.spending_service import (
    SpendingService,
)
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)


def main():

    db = SessionLocal()

    try:

        repository = AccountRepository(db)

        service = SpendingService(
            repository
        )

        result = service.get_spending_summary(
            account_id=1,
            category="Restaurant",
        )

        pprint(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()