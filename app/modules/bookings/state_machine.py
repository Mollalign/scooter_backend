from app.core.constants import BookingStatus
from app.core.exceptions import InvalidStateTransitionException

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    BookingStatus.PENDING_PAYMENT: {
        BookingStatus.CONFIRMED,
        BookingStatus.EXPIRED,
        BookingStatus.CANCELLED,
    },
    BookingStatus.CONFIRMED: {
        BookingStatus.ACTIVE,
        BookingStatus.CANCELLED,
    },
    BookingStatus.ACTIVE: {
        BookingStatus.COMPLETED,
    },
}


def validate_transition(from_status: str, to_status: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise InvalidStateTransitionException(from_status, to_status)
