"""
Model registry — imported by Alembic's env.py to populate Base.metadata.

Every new model file MUST be re-exported here.
"""

from app.models.base import Base, TimestampMixin, UUIDMixin

from app.models.customer import Customer, CustomerDocument, OTPVerification
from app.models.staff import Staff
from app.models.zone import ParkingZone, GeofenceZone
from app.models.pricing import PricingPlan
from app.models.scooter import Scooter
from app.models.iot import IoTDevice, IoTCommand
from app.models.reservation import Reservation
from app.models.ride import Ride, RideEvent, RidePing
from app.models.wallet import (
    CustomerWallet,
    WalletTransaction,
    ChapaTopup,
    PaymentWebhookEvent,
    Withdrawal,
)
from app.models.operations import (
    BatterySwapStation,
    MaintenanceTask,
    BatterySwapTask,
    Incident,
)
from app.models.promo import PromoCode, PromoRedemption
from app.models.notification import Notification
from app.models.audit import AdminAuditLog, SystemConfig

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Identity
    "Customer",
    "CustomerDocument",
    "OTPVerification",
    "Staff",
    # Zones / geo
    "ParkingZone",
    "GeofenceZone",
    # Fleet
    "Scooter",
    "IoTDevice",
    "IoTCommand",
    "PricingPlan",
    # Ride lifecycle
    "Reservation",
    "Ride",
    "RideEvent",
    "RidePing",
    # Money
    "CustomerWallet",
    "WalletTransaction",
    "ChapaTopup",
    "PaymentWebhookEvent",
    "Withdrawal",
    # Ops
    "BatterySwapStation",
    "MaintenanceTask",
    "BatterySwapTask",
    "Incident",
    # Promotions
    "PromoCode",
    "PromoRedemption",
    # Cross-cutting
    "Notification",
    "AdminAuditLog",
    "SystemConfig",
]
