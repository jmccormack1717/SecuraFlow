# SecuraFlow Setup Guide

Complete setup instructions for SecuraFlow.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker)
- pip and npm

## Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and set your database URL:
```
DATABASE_URL=postgresql://user:password@localhost/securaflow
```

5. **Set up PostgreSQL database:**
```bash
# Create database
createdb securaflow

# Or using psql:
psql -U postgres
CREATE DATABASE securaflow;
```

6. **Initialize database tables:**
```bash
python init_db.py
```

7. **Train ML model:**
```bash
python ml/train.py
```

This will create `models/anomaly_detector_v1.pkl` and `models/scaler_v1.pkl`.

8. **Run the backend server:**
```bash
python run.py
# Or: uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set up environment variables:**
```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:8000
```

4. **Run development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Docker Setup (Alternative)

1. **Run with Docker Compose:**
```bash
docker-compose up
```

This will start:
- PostgreSQL database
- Backend API

2. **Train model (still need to do this):**
```bash
docker-compose exec backend python ml/train.py
```

## Testing the System

1. **Start backend and frontend** (see above)

2. **Generate traffic** (in a new terminal):
```bash
cd traffic-generator
pip install -r requirements.txt
python generator.py 10 60 0.05
```

This will:
- Send 10 requests per second
- For 60 seconds
- With 5% anomaly rate

3. **View dashboard:**
- Open `http://localhost:3000`
- You should see traffic metrics and detected anomalies

## API Testing

Test the API directly:

```bash
# Health check
curl http://localhost:8000/api/health

# Send traffic data
curl -X POST http://localhost:8000/api/traffic \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/api/test",
    "method": "GET",
    "status_code": 200,
    "response_time_ms": 50
  }'

# Get metrics
curl http://localhost:8000/api/metrics

# Get anomalies
curl http://localhost:8000/api/anomalies
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify database exists: `psql -l | grep securaflow`

### Model Not Loading
- Ensure you've run `python ml/train.py`
- Check that `models/anomaly_detector_v1.pkl` exists
- Check MODEL_PATH in `.env`

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check VITE_API_URL in frontend `.env`
- Check CORS settings in backend `config.py`

## Next Steps

- Customize anomaly detection threshold
- Add more features to the ML model
- Enhance dashboard visualizations
- Add authentication
- Deploy to Render

