"""The yard's own day: midnight to midnight in Lagos (DECISIONS #47)."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

YARD_TZ = ZoneInfo("Africa/Lagos")


def day_start(day: date) -> datetime:
    """Return the moment the yard's day begins: midnight in Lagos."""
    return datetime.combine(day, time.min, tzinfo=YARD_TZ)


def day_window(day: date) -> tuple[datetime, datetime]:
    """Return the yard's day as a half-open window: [midnight, next midnight)."""
    return day_start(day), day_start(day + timedelta(days=1))