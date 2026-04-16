from datetime import datetime, timezone, timedelta

EAT_OFFSET = timedelta(hours=3)
EAT = timezone(EAT_OFFSET)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_to_eat(dt: datetime) -> datetime:
    return dt.astimezone(EAT)


def eat_to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)
