"""
Central enum registry.

Every status / type string used in the DB lives here. CHECK constraints on
model columns should reference these values. Keeping them in one file makes
schema migrations and cross-module refactors safe.
"""

from enum import StrEnum


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    BLOCKED_UNPAID = "blocked_unpaid"


class StaffRole(StrEnum):
    FIELD_OPERATOR = "field_operator"
    FLEET_MANAGER = "fleet_manager"
    COMPANY_ADMIN = "company_admin"
    SUPER_ADMIN = "super_admin"
    FINANCE = "finance"


class StaffStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class DocumentType(StrEnum):
    NATIONAL_ID_FRONT = "national_id_front"
    NATIONAL_ID_BACK = "national_id_back"
    KEBELE_ID = "kebele_id"
    DRIVERS_LICENSE = "drivers_license"
    SELFIE_WITH_ID = "selfie_with_id"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OTPPurpose(StrEnum):
    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    PHONE_CHANGE = "phone_change"


class Language(StrEnum):
    AMHARIC = "am"
    ENGLISH = "en"


class VehicleType(StrEnum):
    SCOOTER = "scooter"
    BIKE = "bike"
    MOPED = "moped"


class ScooterStatus(StrEnum):
    INACTIVE = "inactive"
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_RIDE = "in_ride"
    LOW_BATTERY = "low_battery"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    LOST = "lost"
    RETIRED = "retired"


class GeofenceType(StrEnum):
    SERVICE_AREA = "service_area"
    NO_PARKING = "no_parking"
    SLOW_SPEED = "slow_speed"
    NO_RIDE = "no_ride"
    PROMO_BONUS = "promo_bonus"


class IoTCommandType(StrEnum):
    UNLOCK = "unlock"
    LOCK = "lock"
    BEEP = "beep"
    DISABLE = "disable"
    REBOOT = "reboot"
    UPDATE_FIRMWARE = "update_firmware"
    LOCATE = "locate"


class IoTCommandStatus(StrEnum):
    SENT = "sent"
    ACK = "ack"
    NACK = "nack"
    TIMEOUT = "timeout"
    FAILED = "failed"


class IoTCommandTrigger(StrEnum):
    RIDE_UNLOCK = "ride_unlock"
    RIDE_END = "ride_end"
    ADMIN = "admin"
    AUTO_SAFETY = "auto_safety"
    MAINTENANCE = "maintenance"


class ReservationStatus(StrEnum):
    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RideStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"
    FORCE_ENDED = "force_ended"
    LOST_SIGNAL = "lost_signal"
    DISPUTED = "disputed"
    SETTLED_UNPAID = "settled_unpaid"


class RideEndReason(StrEnum):
    CUSTOMER = "customer"
    AUTO_TIMEOUT = "auto_timeout"
    ADMIN = "admin"
    LOW_BATTERY = "low_battery"
    SAFETY = "safety"
    INCIDENT = "incident"


class RideEventType(StrEnum):
    CREATED = "created"
    UNLOCK_SENT = "unlock_sent"
    UNLOCK_ACK = "unlock_ack"
    UNLOCK_FAILED = "unlock_failed"
    PAUSED = "paused"
    RESUMED = "resumed"
    ENDING_REQUESTED = "ending_requested"
    LOCK_SENT = "lock_sent"
    LOCK_ACK = "lock_ack"
    ENDED = "ended"
    FORCE_ENDED = "force_ended"
    LOST_SIGNAL = "lost_signal"
    SIGNAL_RESTORED = "signal_restored"
    CHARGE_ATTEMPTED = "charge_attempted"
    CHARGE_SUCCEEDED = "charge_succeeded"
    CHARGE_INSUFFICIENT = "charge_insufficient"
    INCIDENT_REPORTED = "incident_reported"
    GEOFENCE_VIOLATION = "geofence_violation"


class WalletTxType(StrEnum):
    TOPUP = "topup"
    RIDE_CHARGE = "ride_charge"
    REFUND = "refund"
    PROMO_CREDIT = "promo_credit"
    MANUAL_ADJUSTMENT_CREDIT = "manual_adjustment_credit"
    MANUAL_ADJUSTMENT_DEBIT = "manual_adjustment_debit"
    WITHDRAW = "withdraw"
    LATE_FEE = "late_fee"
    RESERVATION_FEE = "reservation_fee"


class LedgerDirection(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class ChapaTopupStatus(StrEnum):
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ChapaPaymentMethod(StrEnum):
    TELEBIRR = "telebirr"
    CBE_BIRR = "cbe_birr"
    AMOLE = "amole"
    CARD = "card"


class WithdrawalStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class WithdrawalMethod(StrEnum):
    TELEBIRR = "telebirr"
    CBE_BIRR = "cbe_birr"
    BANK_TRANSFER = "bank_transfer"


class WebhookProcessingStatus(StrEnum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MaintenanceType(StrEnum):
    REPAIR = "repair"
    RELOCATE = "relocate"
    CHARGE = "charge"
    RETRIEVE = "retrieve"
    CLEAN = "clean"
    INSPECTION = "inspection"


class IncidentType(StrEnum):
    ACCIDENT = "accident"
    DAMAGE = "damage"
    THEFT = "theft"
    BROKEN = "broken"
    ABANDONED = "abandoned"
    MISCONDUCT = "misconduct"
    OTHER = "other"


class IncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class PromoKind(StrEnum):
    FIXED_CREDIT = "fixed_credit"
    PERCENT_OFF_RIDE = "percent_off_ride"
    FREE_MINUTES = "free_minutes"
    SIGNUP_BONUS = "signup_bonus"


class NotificationChannel(StrEnum):
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"
    INAPP = "inapp"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class ActorType(StrEnum):
    CUSTOMER = "customer"
    STAFF = "staff"
    SYSTEM = "system"
    IOT = "iot"
