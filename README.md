# rent_checker

Prototype of a Flask + PostgreSQL single-page app for room rent tracking.

## What it does

- Shows a building plan as room squares in a dark-themed dashboard.
- Computes room status from payment data:
  - Green: current month paid.
  - Yellow: current month unpaid.
  - Red: overdue payment exists.
- Each room has a dropdown with payment history.
- Seeds demo data on first run.

## Run with Docker (recommended)

```bash
docker compose up --build
```

Open `http://localhost:5000`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://rent_user:rent_pass@localhost:5432/rent_checker
python run.py
```

## Playwright tests

```bash
pip install -r requirements.txt
python -m playwright install chromium
pytest
```

Tests are in `tests/e2e/test_rent_checker.py` and validate:
- room rendering + mixed statuses;
- dropdown history behavior.
