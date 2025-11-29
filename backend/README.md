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
- `GET /api/metrics` - Get aggregated metrics (supports time range filtering)
- `GET /api/anomalies` - Get detected anomalies (supports pagination and filtering)
- `GET /api/health` - Health check endpoint
- `POST /api/demo/generate` - Generate demo traffic data
  - Query params: `count` (1-1000), `anomaly_rate` (0.0-1.0), `hours_back` (1-168)

## API Documentation

When running locally, visit `http://localhost:8000/docs` for interactive API documentation.

Live API docs: [https://securaflow-backend-9ihj.onrender.com/docs](https://securaflow-backend-9ihj.onrender.com/docs)

## Development

Run with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

