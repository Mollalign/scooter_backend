"""Timezone helpers. Store UTC, present as East Africa Time."""

from datetime import datetime, timedelta, timezone

EAT = timezone(timedelta(hours=3), name="EAT")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_eat(dt: datetime) -> datetime:
    return dt.astimezone(EAT)


def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)
