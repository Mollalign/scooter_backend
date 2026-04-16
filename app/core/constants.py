from enum import StrEnum


class UserRole(StrEnum):
    CUSTOMER = "customer"
    OWNER = "owner"
    BOTH = "both"
    ADMIN = "admin"


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class DocumentType(StrEnum):
    NATIONAL_ID_FRONT = "national_id_front"
    NATIONAL_ID_BACK = "national_id_back"
    SCOOTER_REGISTRATION = "scooter_registration"
    KEBELE_ID = "kebele_id"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ScooterStatus(StrEnum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    UNLISTED = "unlisted"


class BookingStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentStatus(StrEnum):
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentProvider(StrEnum):
    CHAPA = "chapa"
    CASH = "cash"


class PaymentMethod(StrEnum):
    TELEBIRR = "telebirr"
    CBE_BIRR = "cbe_birr"
    AMOLE = "amole"
    CASH = "cash"


class RefundStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PayoutStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LedgerEntryType(StrEnum):
    EARNING_CREDIT = "earning_credit"
    REFUND_DEBIT = "refund_debit"
    PAYOUT_DEBIT = "payout_debit"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class LedgerDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class NotificationChannel(StrEnum):
    SMS = "sms"
    PUSH = "push"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OTPPurpose(StrEnum):
    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"


class WebhookProcessingStatus(StrEnum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"
