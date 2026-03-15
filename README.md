# Tourism Recommendation API

A production-ready FastAPI application for tourist place recommendations using Machine Learning (NearestNeighbors) with OpenStreetMap Overpass API fallback.

## Features

- **ML Model**: Uses scikit-learn NearestNeighbors for cities in dataset
- **Overpass API Fallback**: Fetches from OpenStreetMap for unknown cities
- **Health Check**: `/health` endpoint for monitoring
- **API Documentation**: Auto-generated at `/docs` (Swagger UI)
- **Dockerized**: Ready for Google Cloud Run deployment

## Project Structure

```
tourism-recommendation/
├── app/
│   └── main.py              # FastAPI application
├── Top Indian Places to Visit.csv  # Dataset (place this file in root)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md              # This file
```

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

The API will be available at `http://localhost:8080`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/cities` | GET | List cities in dataset |
| `/recommend/{city}` | GET | Get recommendations |
| `/docs` | GET | Swagger UI documentation |

## Testing the API

### Using Browser

1. **API Root**: `http://localhost:8080/`
2. **Swagger UI**: `http://localhost:8080/docs`
3. **Recommendations**: `http://localhost:8080/recommend/hyderabad`
4. **Health Check**: `http://localhost:8080/health`
5. **Cities List**: `http://localhost:8080/cities`

### Using curl

```bash
# Health check
curl http://localhost:8080/health

# Get recommendations for Hyderabad (dataset city)
curl http://localhost:8080/recommend/hyderabad

# Get recommendations for Delhi (dataset city)
curl http://localhost:8080/recommend/delhi

# Get recommendations for unknown city (Overpass API)
curl http://localhost:8080/recommend/pune

# List all cities in dataset
curl http://localhost:8080/cities
```

## Google Cloud Run Deployment

### Prerequisites

1. [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project YOUR_PROJECT_ID`
4. Enable APIs:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

### Deployment Steps

#### Option 1: Using gcloud CLI (Build & Deploy)

```bash
# Navigate to project directory
cd c:\famousplaces

# Build and deploy in one command
gcloud run deploy tourism-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 10 \
  --timeout 300
```

#### Option 2: Using Cloud Build (Recommended for Production)

```bash
# Submit build to Cloud Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/tourism-api

# Deploy to Cloud Run
gcloud run deploy tourism-api \
  --image gcr.io/YOUR_PROJECT_ID/tourism-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

#### Option 3: Local Docker Build & Push

```bash
# Build Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/tourism-api .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/tourism-api

# Deploy to Cloud Run
gcloud run deploy tourism-api \
  --image gcr.io/YOUR_PROJECT_ID/tourism-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### After Deployment

Once deployed, Cloud Run will provide a URL like:
`https://tourism-api-abc123-uc.a.run.app`

**Test the deployed API:**

```bash
# Replace with your actual Cloud Run URL
BASE_URL="https://tourism-api-xxx-uc.a.run.app"

curl $BASE_URL/health

curl $BASE_URL/recommend/hyderabad

curl $BASE_URL/recommend/delhi
```

## Response Format

### ML Model Response (city in dataset)

```json
{
  "city": "Hyderabad",
  "source": "ml_model",
  "count": 5,
  "places": [
    {
      "name": "Charminar",
      "city": "Hyderabad",
      "type": "Historical",
      "rating": 4.5,
      "significance": "Heritage"
    }
  ]
}
```

### Overpass API Response (unknown city)

```json
{
  "city": "Pune",
  "source": "overpass_api",
  "count": 10,
  "places": [
    {
      "name": "Shaniwar Wada",
      "tourism_type": "attraction",
      "latitude": 18.5195,
      "longitude": 73.8553
    }
  ]
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8080 |

## Production Optimizations

1. **Logging**: Structured logging with timestamps
2. **Error Handling**: Comprehensive exception handling with HTTP status codes
3. **Pydantic Models**: Request/response validation
4. **Health Checks**: `/health` endpoint for load balancers
5. **Graceful Degradation**: Works without dataset (Overpass API only)
6. **Case-Insensitive Search**: City names matched case-insensitively
7. **Exponential Backoff**: Geocoding retries with increasing delays

## Troubleshooting

### Dataset Not Found
Ensure `Top Indian Places to Visit.csv` is in the project root before building the Docker image.

### Overpass API Timeout
The API has a 15-second timeout. For slow connections, increase `TIMEOUT` in `OverpassService` class.

### Geocoding Failures
Geocoding uses Nominatim with retry logic (3 attempts). If consistently failing, check internet connectivity.

## License

MIT
