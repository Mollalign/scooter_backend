import random
from datetime import datetime, timezone


def generate_booking_number() -> str:
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    random_part = f"{random.randint(0, 9999):04d}"
    return f"BK-{date_part}-{random_part}"
