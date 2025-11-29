# SecuraFlow

Real-time API monitoring and anomaly detection system. A full-stack application combining FastAPI backend, React frontend, and ML-based anomaly detection.

🌐 **Live Demo**: [https://securaflow-frontend.onrender.com](https://securaflow-frontend.onrender.com)

## Features

- **Real-time Traffic Monitoring**: Process and analyze API traffic in real-time
- **ML-based Anomaly Detection**: Detect anomalies using machine learning models (Isolation Forest)
- **Interactive Dashboard**: React-based dashboard with real-time visualizations and metrics
- **Dark Mode Support**: Toggle between light and dark themes with system preference detection
- **Demo Data Generation**: One-click demo data generation for testing and demonstrations
- **Production Ready**: Docker containerization, CI/CD setup, and deployed on Render

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
- `POST /api/demo/generate` - Generate demo traffic data (for testing)

See the [API documentation](https://securaflow-backend-9ihj.onrender.com/docs) for detailed endpoint information.

## Project Structure

```
securaflow/
├── backend/
│   ├── app/           # FastAPI application
│   │   ├── api/       # API routes
│   │   ├── database/  # Database models and setup
│   │   ├── services/  # Business logic (anomaly detection, feature extraction)
│   │   └── models/    # Pydantic schemas
│   ├── ml/            # ML training scripts
│   └── models/        # Trained models
├── frontend/          # React + TypeScript application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── contexts/    # React contexts (Theme)
│   └── public/         # Static assets
├── traffic-generator/  # Traffic generation script for testing
└── .github/           # CI/CD workflows
```

## Deployment

The application is deployed on Render:
- **Frontend**: [https://securaflow-frontend.onrender.com](https://securaflow-frontend.onrender.com)
- **Backend API**: [https://securaflow-backend-9ihj.onrender.com](https://securaflow-backend-9ihj.onrender.com)
- **API Docs**: [https://securaflow-backend-9ihj.onrender.com/docs](https://securaflow-backend-9ihj.onrender.com/docs)

## Usage

### Using the Live Demo

1. Visit the [live demo](https://securaflow-frontend.onrender.com)
2. Click "Generate Demo Data" on the dashboard to populate with sample traffic
3. Explore the dashboard, metrics, and anomalies pages
4. Toggle dark mode using the sun/moon icon in the header

### Local Development

See [SETUP.md](SETUP.md) for detailed local setup instructions.

## License

MIT

