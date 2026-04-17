"""Short human-readable identifiers for rides, transactions, etc."""

import secrets
from datetime import datetime, timezone

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no O, 0, 1, I


def _suffix(n: int = 6) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))


def new_ride_number() -> str:
    return f"R-{datetime.now(timezone.utc):%y%m%d}-{_suffix(5)}"


def new_tx_ref() -> str:
    return f"GF-{datetime.now(timezone.utc):%y%m%d%H%M%S}-{_suffix(6)}"


def new_idempotency_key() -> str:
    return secrets.token_urlsafe(24)
