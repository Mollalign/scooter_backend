# GreenFlow Mobility — Backend

Single-tenant ride-sharing backend for a scooter/e-bike rental business
(inspired by FASTeco). One company operates a fleet of IoT-enabled vehicles;
riders unlock via QR, pay from a prepaid wallet (Chapa top-up), and return
the vehicle within service-area geofences.

---

## Tech stack

| Layer           | Choice                                            |
|-----------------|---------------------------------------------------|
| Runtime         | Python 3.12, FastAPI, Uvicorn                     |
| ORM / DB        | SQLAlchemy 2 (async) + Alembic + PostgreSQL 15    |
| Geo             | PostGIS + GeoAlchemy2                             |
| Auth            | JWT (access + refresh), bcrypt                    |
| Payments        | Chapa (Telebirr, CBE Birr, Amole, Card)           |
| Push / SMS      | FCM, AfroMessage (or any HTTP SMS provider)       |
| Object storage  | S3-compatible (DO Spaces / R2 / MinIO / AWS)      |
| IoT             | MQTT broker (optional HTTP fallback for MVP)      |
| Background jobs | APScheduler (in-process)                          |

---

## Folder structure

```text
scooter_backend/
├── alembic/                    # DB migrations
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── main.py                 # FastAPI entry + lifespan
│   │
│   ├── core/                   # cross-cutting infrastructure
│   │   ├── config.py           # Pydantic settings
│   │   ├── database.py         # async engine + session factory
│   │   ├── security.py         # JWT + bcrypt
│   │   ├── deps.py             # FastAPI dependencies (auth, db)
│   │   ├── permissions.py      # staff role guards
│   │   ├── exceptions.py       # domain exception classes
│   │   ├── exception_handlers.py
│   │   ├── pagination.py
│   │   ├── logging.py
│   │   └── enums.py            # every status / type enum
│   │
│   ├── models/                 # SQLAlchemy ORM (flat, per-domain)
│   │   ├── base.py             # Base, UUIDMixin, TimestampMixin
│   │   ├── customer.py         # customers, customer_documents, otp_verifications
│   │   ├── staff.py
│   │   ├── wallet.py           # wallets, ledger, Chapa top-ups, webhooks, withdrawals
│   │   ├── zone.py             # parking zones + geofence polygons
│   │   ├── scooter.py
│   │   ├── iot.py              # devices + command audit log
│   │   ├── pricing.py
│   │   ├── reservation.py
│   │   ├── ride.py             # rides, ride_events, ride_pings
│   │   ├── operations.py       # maintenance_tasks, battery_swap_tasks, incidents
│   │   ├── promo.py
│   │   ├── notification.py
│   │   └── audit.py            # admin_audit_logs, system_configs
│   │
│   ├── api/                    # HTTP layer
│   │   ├── router.py           # aggregates all v1 routers
│   │   └── v1/                 # feature-sliced modules
│   │       ├── auth/           # OTP, register, login, refresh
│   │       ├── customers/      # /me profile + documents
│   │       ├── wallet/         # balance, Chapa top-up, history, withdrawals
│   │       ├── zones/          # parking zones + geofences (public)
│   │       ├── scooters/       # nearby, scan-by-QR
│   │       ├── reservations/   # short-term scooter holds
│   │       ├── rides/          # unlock → pause → resume → end, history
│   │       ├── webhooks/       # Chapa webhook (signed)
│   │       ├── admin/          # staff admin panel
│   │       └── ops/            # field operator / fleet manager
│   │
│   ├── integrations/           # external service clients
│   │   ├── chapa.py
│   │   ├── sms.py
│   │   ├── fcm.py
│   │   ├── s3.py
│   │   └── mqtt.py
│   │
│   ├── workers/                # APScheduler jobs
│   │   ├── scheduler.py
│   │   ├── reservation_expiry.py
│   │   ├── ride_watchdog.py
│   │   ├── chapa_verifier.py
│   │   ├── battery_monitor.py
│   │   └── notification_retry.py
│   │
│   └── utils/                  # tiny helpers
│       ├── phone.py
│       ├── datetime.py
│       ├── ids.py
│       └── geo.py
│
├── tests/                      # pytest + httpx
├── scripts/                    # seed scripts, CLI utilities
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

Each `api/v1/<feature>/` folder follows the same contract:

```
<feature>/
├── __init__.py
├── router.py      # FastAPI endpoints — thin
├── schemas.py     # Pydantic request / response models
└── service.py     # business logic, works against models + integrations
```

---

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # fill DATABASE_URL + secrets

# PostgreSQL must have postgis, pgcrypto, btree_gist installed
# (the app will CREATE EXTENSION IF NOT EXISTS on startup)

alembic revision --autogenerate -m "initial schema"
alembic upgrade head

uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the interactive OpenAPI explorer.

---

## Ride lifecycle (happy path)

```
 customer opens app
        │
        ▼
 GET /scooters/nearby           → map of free scooters
        │
        ▼
 POST /reservations             (optional, 10-min hold)
        │
        ▼
 POST /rides/unlock             → wallet balance check
                                → IoT unlock command
                                → Ride row created (status=active)
        │
        ├── POST /rides/{id}/pings                (telemetry)
        ├── POST /rides/{id}/pause | resume
        ▼
 POST /rides/{id}/end           → compute fare
                                → debit wallet (ledger + balance)
                                → IoT lock command
                                → Ride.status = ended
```

---

## Roles

| Role              | Auth audience | Scope                                          |
|-------------------|---------------|------------------------------------------------|
| Customer          | `customer`    | Self-service ride lifecycle, wallet, profile   |
| Field operator    | `staff`       | Task queue, incident reports, swap confirms    |
| Fleet manager     | `staff`       | Everything above + IoT commands + force-end    |
| Finance           | `staff`       | Withdrawal approvals, reconciliation           |
| Company admin     | `staff`       | Users, scooters, pricing plans, zones          |
| Super admin       | `staff`       | Root — staff management, system configs        |

Enforcement lives in `app/core/permissions.py`.
