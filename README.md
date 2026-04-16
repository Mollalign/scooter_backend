# Scooter Rental System — Backend API

A two-sided marketplace backend for scooter rentals in Ethiopia, built with FastAPI and PostgreSQL.

## Tech Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 15+ with PostGIS and btree_gist extensions
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT (access + refresh tokens)
- **Payments**: Chapa (Telebirr, CBE Birr, Amole)
- **Background Jobs**: APScheduler

## Prerequisites

- Python 3.12+
- PostgreSQL 15+ with PostGIS and btree_gist extensions
- A Chapa account for payment processing

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env template and configure
cp .env.example .env

# 4. Enable PostgreSQL extensions
psql -U postgres -d scooter_rental -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
psql -U postgres -d scooter_rental -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
psql -U postgres -d scooter_rental -c "CREATE EXTENSION IF NOT EXISTS \"postgis\";"
psql -U postgres -d scooter_rental -c "CREATE EXTENSION IF NOT EXISTS \"btree_gist\";"

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
app/
├── core/          Shared infrastructure (config, DB, auth, permissions)
├── models/        SQLAlchemy ORM models (all 15+ tables)
├── modules/       Business domains (auth, users, scooters, bookings, payments, wallet, notifications, admin)
├── jobs/          Background tasks (booking expiry, payment verification)
└── utils/         Pure utility functions (phone normalization, datetime, etc.)
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
