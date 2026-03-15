import os
import sys
import logging
import time
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager

import pandas as pd
import requests
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sklearn.neighbors import NearestNeighbors
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Pydantic Models for Request/Response
# ============================================

class PlaceRecommendation(BaseModel):
    name: str
    city: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[float] = None

class MLPlace(BaseModel):
    Name: str
    City: str
    Type: str
    Google_review_rating: float

class RecommendationResponse(BaseModel):
    city: str
    source: str
    count: int
    places: List[Dict[str, Any]]

class ErrorResponse(BaseModel):
    detail: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    dataset_size: int


# ============================================
# Global Variables for Model and Data
# ============================================

df: Optional[pd.DataFrame] = None
model: Optional[NearestNeighbors] = None
cities_in_dataset: set = set()


# ============================================
# Dataset Loading and Model Training
# ============================================

def load_dataset() -> pd.DataFrame:
    """Load and preprocess the tourism dataset."""
    csv_path = "Top Indian Places to Visit.csv"
    
    # Try multiple paths for flexibility
    possible_paths = [
        csv_path,
        os.path.join("app", csv_path),
        os.path.join("..", csv_path),
        os.path.join("/app", csv_path),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Loading dataset from: {path}")
            df = pd.read_csv(path)
            break
    else:
        raise FileNotFoundError(f"Dataset not found. Searched: {possible_paths}")
    
    # Select relevant columns
    required_cols = ['City', 'Name', 'Type', 'Google review rating', 'Significance']
    
    # Check if columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing columns: {missing_cols}")
        logger.info(f"Available columns: {df.columns.tolist()}")
        # Use available columns
        available_cols = [col for col in required_cols if col in df.columns]
        df = df[available_cols]
    else:
        df = df[required_cols]
    
    # Drop rows with missing values
    df = df.dropna()
    
    logger.info(f"Dataset loaded: {len(df)} records")
    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical features for ML model."""
    df = df.copy()
    
    # Encode categorical columns
    if 'City' in df.columns:
        df['City_encoded'] = df['City'].astype('category').cat.codes
    if 'Type' in df.columns:
        df['Type_encoded'] = df['Type'].astype('category').cat.codes
    if 'Significance' in df.columns:
        df['Sig_encoded'] = df['Significance'].astype('category').cat.codes
    else:
        df['Sig_encoded'] = 0
    
    return df


def train_model(df: pd.DataFrame) -> NearestNeighbors:
    """Train the NearestNeighbors model."""
    # Select feature columns
    feature_cols = ['City_encoded', 'Type_encoded', 'Sig_encoded', 'Google review rating']
    
    # Filter to only existing columns
    available_features = [col for col in feature_cols if col in df.columns]
    
    if len(available_features) < 2:
        raise ValueError(f"Insufficient features for training. Available: {available_features}")
    
    features = df[available_features]
    
    # Train NearestNeighbors model
    n_neighbors = min(5, len(df))
    model = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
    model.fit(features)
    
    logger.info(f"Model trained with {n_neighbors} neighbors, {len(df)} samples")
    return model


# ============================================
# Geocoding Service
# ============================================

class GeocodingService:
    def __init__(self, user_agent: str = "tourism_recommendation_api"):
        self.geolocator = Nominatim(user_agent=user_agent)
    
    def get_coordinates(self, city: str, country: str = "India") -> tuple:
        """Get latitude and longitude for a city."""
        search_query = f"{city}, {country}"
        
        for attempt in range(3):
            try:
                location = self.geolocator.geocode(search_query, timeout=10)
                
                if location:
                    logger.info(f"Geocoded '{city}': ({location.latitude}, {location.longitude})")
                    return location.latitude, location.longitude
                else:
                    logger.warning(f"Geocoding returned no results for '{city}'")
                    
            except GeocoderTimedOut:
                logger.warning(f"Geocoding timeout (attempt {attempt + 1}/3)")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except GeocoderUnavailable:
                logger.warning(f"Geocoder unavailable (attempt {attempt + 1}/3)")
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Geocoding error: {e}")
                break
        
        return None, None


geocoding_service = GeocodingService()


# ============================================
# Overpass API Service
# ============================================

class OverpassService:
    BASE_URL = "https://overpass-api.de/api/interpreter"
    TIMEOUT = 15
    
    def fetch_tourism_places(self, lat: float, lon: float, radius: int = 10000) -> List[Dict[str, Any]]:
        """Fetch tourism places from OpenStreetMap using Overpass API."""
        
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"](around:{radius},{lat},{lon});
          way["tourism"](around:{radius},{lat},{lon});
          relation["tourism"](around:{radius},{lat},{lon});
        );
        out center tags 10;
        """
        
        try:
            response = requests.post(
                self.BASE_URL,
                data={"data": query},
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            places = []
            
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                name = tags.get("name")
                
                if name:
                    place_info = {
                        "name": name,
                        "tourism_type": tags.get("tourism", "unknown"),
                        "latitude": element.get("lat") or element.get("center", {}).get("lat"),
                        "longitude": element.get("lon") or element.get("center", {}).get("lon")
                    }
                    places.append(place_info)
            
            logger.info(f"Fetched {len(places)} places from Overpass API")
            return places[:10]  # Return top 10
            
        except requests.exceptions.Timeout:
            logger.error("Overpass API timeout")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Overpass API error: {e}")
            return []


overpass_service = OverpassService()


# ============================================
# Recommendation Engine
# ============================================

def get_ml_recommendations(city_name: str) -> List[Dict[str, Any]]:
    """Get recommendations using the ML model."""
    global df, model
    
    if df is None or model is None:
        raise RuntimeError("Model not initialized")
    
    # Get city encoding
    city_rows = df[df['City'].str.lower() == city_name.lower()]
    
    if city_rows.empty:
        city_rows = df[df['City'].str.contains(city_name, case=False, na=False)]
    
    if city_rows.empty:
        return []
    
    sample = city_rows.iloc[0]
    
    # Build input vector
    input_vector = []
    for col in ['City_encoded', 'Type_encoded', 'Sig_encoded', 'Google review rating']:
        if col in df.columns:
            input_vector.append(sample[col])
        else:
            input_vector.append(0)
    
    # Get recommendations
    distances, indices = model.kneighbors([input_vector])
    
    # Build results
    results = []
    for idx in indices[0]:
        row = df.iloc[idx]
        result = {
            "name": str(row.get('Name', 'Unknown')),
            "city": str(row.get('City', 'Unknown')),
            "type": str(row.get('Type', 'Unknown')),
            "rating": float(row.get('Google review rating', 0)) if pd.notna(row.get('Google review rating')) else None,
            "significance": str(row.get('Significance', 'Unknown')) if 'Significance' in row else None
        }
        results.append(result)
    
    return results


def get_internet_recommendations(city_name: str) -> List[Dict[str, Any]]:
    """Get recommendations from OpenStreetMap Overpass API."""
    lat, lon = geocoding_service.get_coordinates(city_name)
    
    if lat is None or lon is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not geocode city: {city_name}"
        )
    
    places = overpass_service.fetch_tourism_places(lat, lon)
    
    if not places:
        raise HTTPException(
            status_code=404,
            detail=f"No tourist places found for city: {city_name}"
        )
    
    return places


def recommend_places(city_name: str) -> tuple:
    """
    Main recommendation function.
    Returns: (places_list, source_string)
    """
    global cities_in_dataset
    
    city_lower = city_name.lower()
    
    # Check if city exists in dataset (case-insensitive)
    city_in_dataset = any(city_lower == c.lower() for c in cities_in_dataset)
    
    if city_in_dataset and df is not None and model is not None:
        logger.info(f"Using ML model for city: {city_name}")
        places = get_ml_recommendations(city_name)
        if places:
            return places, "ml_model"
    
    # Fallback to internet search
    logger.info(f"Using Overpass API for city: {city_name}")
    places = get_internet_recommendations(city_name)
    return places, "overpass_api"


# ============================================
# FastAPI Application
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    global df, model, cities_in_dataset
    
    # Startup
    logger.info("Starting up Tourism Recommendation API...")
    
    try:
        # Load dataset and train model
        df = load_dataset()
        df = encode_features(df)
        model = train_model(df)
        
        # Build city index
        if 'City' in df.columns:
            cities_in_dataset = set(df['City'].unique())
        
        logger.info(f"Startup complete. {len(cities_in_dataset)} cities in dataset.")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Continue without dataset - will use Overpass API only
        df = None
        model = None
        cities_in_dataset = set()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Tourism Recommendation API",
    description="ML-powered tourism recommendation API with OpenStreetMap fallback",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite default
        "https://*",              # Allow all HTTPS (production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API Endpoints
# ============================================

@app.get("/", response_model=Dict[str, str])
def home():
    """Root endpoint."""
    return {
        "message": "Tourism Recommendation API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "dataset_size": len(df) if df is not None else 0
    }


@app.get("/cities")
def list_cities():
    """List all cities available in the dataset."""
    return {
        "cities": sorted(list(cities_in_dataset)),
        "count": len(cities_in_dataset)
    }


@app.get("/recommend/{city}", response_model=RecommendationResponse)
def get_recommendation(city: str):
    """
    Get tourist place recommendations for a city.
    
    - If city exists in dataset: uses ML model
    - If city not in dataset: fetches from OpenStreetMap Overpass API
    """
    if not city or not city.strip():
        raise HTTPException(status_code=400, detail="City name cannot be empty")
    
    city = city.strip()
    
    try:
        places, source = recommend_places(city)
        
        return {
            "city": city,
            "source": source,
            "count": len(places),
            "places": places
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recommending places for '{city}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing request: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
