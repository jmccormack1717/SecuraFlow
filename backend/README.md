# SecuraFlow Backend

Real-time API monitoring and anomaly detection backend service.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from `.env.example` and configure:
```bash
cp .env.example .env
```

3. Set up PostgreSQL database and update `DATABASE_URL` in `.env`

4. Run database migrations (create tables):
```python
from app.database.base import Base, engine
Base.metadata.create_all(bind=engine)
```

5. Train ML model (see `ml/train.py`)

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/traffic` - Ingest traffic data
- `GET /api/metrics` - Get aggregated metrics
- `GET /api/anomalies` - Get detected anomalies
- `GET /api/health` - Health check

## Development

Run with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

