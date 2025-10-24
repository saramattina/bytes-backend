# Backend Setup

## Prerequisites
- Python 3.9+
- pip (comes with Python)
- (Optional) virtualenv / venv module

## 1. Create and activate a virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## 2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure environment variables
- Duplicate `backend/.env` (or create one) and fill in your AWS, database, and Django settings.
- Ensure the values match your deployment/storage configuration.

## 4. Apply migrations and run the server
```bash
python manage.py migrate
python manage.py runserver
```

## Optional
- If you need a fresh database, delete `db.sqlite3` and rerun `migrate`.
- `create-database.sql` is provided as a helper script (not required for Django migrations).

