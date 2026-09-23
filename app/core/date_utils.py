from datetime import datetime


def get_current_month_range(
    now: datetime | None = None,
) -> tuple[datetime, datetime]:

    if now is None:
        now = datetime.now()

    start = datetime(
        year=now.year,
        month=now.month,
        day=1,
    )

    if now.month == 12:
        end = datetime(
            year=now.year + 1,
            month=1,
            day=1,
        )
    else:
        end = datetime(
            year=now.year,
            month=now.month + 1,
            day=1,
        )

    return start, end