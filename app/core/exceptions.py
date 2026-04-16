class AppException(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=409)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail=detail, status_code=403)


class BookingConflictException(ConflictException):
    def __init__(self):
        super().__init__(detail="Scooter no longer available for the selected time")


class InvalidStateTransitionException(AppException):
    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            detail=f"Cannot transition from '{from_status}' to '{to_status}'",
            status_code=409,
        )


class PaymentVerificationException(AppException):
    def __init__(self, detail: str = "Payment verification failed"):
        super().__init__(detail=detail, status_code=402)
