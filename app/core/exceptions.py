"""Application-specific exceptions mapped to HTTP responses."""


class AppException(Exception):
    status_code: int = 400
    default_detail: str = "Request could not be processed"

    def __init__(self, detail: str | None = None, *, code: str | None = None):
        self.detail = detail or self.default_detail
        self.code = code or self.__class__.__name__
        super().__init__(self.detail)


class NotFoundException(AppException):
    status_code = 404
    default_detail = "Resource not found"


class ConflictException(AppException):
    status_code = 409
    default_detail = "Resource conflict"


class ForbiddenException(AppException):
    status_code = 403
    default_detail = "Access denied"


class UnauthorizedException(AppException):
    status_code = 401
    default_detail = "Authentication required"


class ValidationException(AppException):
    status_code = 422
    default_detail = "Validation failed"


class InvalidStateTransitionException(ConflictException):
    def __init__(self, from_status: str, to_status: str):
        super().__init__(f"Cannot transition from '{from_status}' to '{to_status}'")


# Domain-specific
class InsufficientWalletBalance(AppException):
    status_code = 402
    default_detail = "Insufficient wallet balance"


class ReservationExpiredException(ConflictException):
    default_detail = "Reservation has expired"


class ScooterUnavailableException(ConflictException):
    default_detail = "Scooter is not available"


class OutsideServiceAreaException(ConflictException):
    default_detail = "Location is outside the service area"


class IoTCommandFailedException(AppException):
    status_code = 502
    default_detail = "Scooter did not respond to command"


class ChapaIntegrationError(AppException):
    status_code = 502
    default_detail = "Payment provider error"
