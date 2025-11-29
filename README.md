# SecuraFlow

Real-time API monitoring and anomaly detection system. A full-stack application combining FastAPI backend, React frontend, and ML-based anomaly detection.

🌐 **Live Demo**: [https://securaflow-frontend.onrender.com](https://securaflow-frontend.onrender.com)

## Features

- **Real-time Traffic Monitoring**: Process and analyze API traffic in real-time
- **ML-based Anomaly Detection**: Detect anomalies using machine learning models (Isolation Forest)
- **Interactive Dashboard**: React-based dashboard with real-time visualizations and metrics
- **Model Performance Tracking**: ML model evaluation metrics (precision, recall, F1, confusion matrix)
- **Request Correlation IDs**: Track requests across services with correlation IDs and structured logging
- **Error Boundaries**: Production-ready error handling with React error boundaries
- **Authentication**: JWT-based authentication with signup/login and guest demo access
- **Rate Limiting**: API rate limiting to prevent abuse (60 requests/minute)
- **Dark Mode Support**: Toggle between light and dark themes with system preference detection
- **Demo Data Generation**: One-click demo data generation for testing and demonstrations
- **Production Ready**: Docker containerization, CI/CD setup, comprehensive testing, and deployed on Render

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL
- **Frontend**: React + TypeScript + Tailwind CSS
- **ML**: Scikit-learn (Isolation Forest) for anomaly detection
- **Deployment**: Docker + Render

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        User[Users/Browsers]
        TrafficGen[Traffic Generator Script]
    end

    subgraph "Frontend - React + TypeScript"
        UI[Dashboard UI]
        Components[React Components]
        API_Client[API Client Service]
    end

    subgraph "Backend - FastAPI"
        API[FastAPI Application]
        RateLimit[Rate Limiter]
        CORS[CORS Middleware]
        
        subgraph "API Routes"
            TrafficRoute[/api/traffic]
            MetricsRoute[/api/metrics]
            AnomaliesRoute[/api/anomalies]
            HealthRoute[/api/health]
            DemoRoute[/api/demo/generate]
        end
        
        subgraph "Services"
            FeatureExtractor[Feature Extractor]
            AnomalyDetector[Anomaly Detector]
            Logger[Logging Service]
        end
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        TrafficLogs[Traffic Logs Table]
        Anomalies[Anomalies Table]
        Metrics[Metrics Aggregation]
    end

    subgraph "ML Pipeline"
        MLModel[Isolation Forest Model]
        Scaler[Feature Scaler]
        Training[Training Script]
    end

    subgraph "Deployment"
        Render[Render Platform]
        Docker[Docker Containers]
        CI[GitHub Actions CI/CD]
    end

    %% User interactions
    User -->|HTTP Requests| UI
    UI -->|API Calls| API_Client
    API_Client -->|REST API| API
    
    %% Traffic generation
    TrafficGen -->|POST /api/traffic| TrafficRoute
    
    %% API flow
    API --> RateLimit
    RateLimit --> CORS
    CORS --> TrafficRoute
    CORS --> MetricsRoute
    CORS --> AnomaliesRoute
    CORS --> HealthRoute
    CORS --> DemoRoute
    
    %% Traffic ingestion flow
    TrafficRoute --> FeatureExtractor
    FeatureExtractor --> AnomalyDetector
    AnomalyDetector --> MLModel
    AnomalyDetector --> Scaler
    AnomalyDetector --> PostgreSQL
    
    %% Data storage
    PostgreSQL --> TrafficLogs
    PostgreSQL --> Anomalies
    PostgreSQL --> Metrics
    
    %% Metrics and anomalies retrieval
    MetricsRoute --> PostgreSQL
    AnomaliesRoute --> PostgreSQL
    
    %% ML model training
    Training --> MLModel
    Training --> Scaler
    
    %% Deployment
    CI --> Render
    Render --> Docker
    Docker --> API
    Docker --> PostgreSQL
    
    %% Logging
    API --> Logger
    AnomalyDetector --> Logger

    style User fill:#e1f5ff
    style UI fill:#e1f5ff
    style API fill:#fff4e1
    style PostgreSQL fill:#e8f5e9
    style MLModel fill:#f3e5f5
    style Render fill:#fce4ec
```

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
- `GET /api/model-metrics` - Get ML model performance metrics
- `POST /api/model-metrics/evaluate` - Evaluate current model performance
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/demo` - Get demo guest token (no authentication required)
- `GET /api/auth/me` - Get current authenticated user

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
2. Click **"Continue as Guest"** to access the demo without creating an account
   - Or sign up/login for a full account experience
   - **Note**: On Render's free tier, user accounts and data may be cleared after service restarts or database inactivity. For quick demo access, "Continue as Guest" is recommended.
3. Click "Generate Demo Data" on the dashboard to populate with sample traffic
4. Explore the dashboard, metrics, anomalies, and model performance pages
5. Toggle dark mode using the sun/moon icon in the header

### Local Development

See [SETUP.md](SETUP.md) for detailed local setup instructions.

## License

MIT

