# SecuraFlow

Real-time API monitoring and anomaly detection system. A full-stack application combining FastAPI backend, React frontend, and ML-based anomaly detection.

## Features

- **Real-time Traffic Monitoring**: Process and analyze API traffic in real-time
- **ML-based Anomaly Detection**: Detect anomalies using machine learning models
- **Interactive Dashboard**: React-based dashboard with real-time visualizations
- **Production Ready**: Docker containerization and CI/CD setup

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL
- **Frontend**: React + TypeScript + Tailwind CSS
- **ML**: Scikit-learn (Isolation Forest) for anomaly detection
- **Deployment**: Docker + Render

## Quick Start

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL
```

4. Train ML model:
```bash
python ml/train.py
```

5. Set up database:
```python
from app.database.base import Base, engine
Base.metadata.create_all(bind=engine)
```

6. Run the server:
```bash
uvicorn app.main:app --reload
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

### Docker

Run with Docker Compose:
```bash
docker-compose up
```

## API Endpoints

- `POST /api/traffic` - Ingest traffic data
- `GET /api/metrics` - Get aggregated metrics
- `GET /api/anomalies` - Get detected anomalies
- `GET /api/health` - Health check

## Project Structure

```
securaflow/
├── backend/
│   ├── app/           # FastAPI application
│   ├── ml/            # ML training scripts
│   └── models/        # Trained models
├── frontend/          # React application
└── .github/          # CI/CD workflows
```

## License

MIT

