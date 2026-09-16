from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# --- App Content (Events) Schemas ---
# (These are unchanged)
class EventBase(BaseModel):
    event_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    recommendation_reason: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    # ... other optional fields

class Event(EventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Core API Schemas (Final Version) ---
class StateTourismStatsBase(BaseModel):
    state: str
    year: int
    
    # Columns from the final predictions.csv
    visitors_000: Optional[float] = None
    expected_visitors_000: Optional[float] = None
    actual_share_pct: Optional[float] = None
    expected_share_pct: Optional[float] = None
    opportunity_gap_pp: Optional[float] = None
    opportunity_gap_pct: Optional[float] = None
    is_holdout_year: Optional[bool] = None
    naive_forecast_next_year_000: Optional[float] = None

class StateTourismStats(StateTourismStatsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Legacy Recommendation Schemas ---
# (These are unchanged)
class RecommendationRequest(BaseModel):
    lat: float
    lng: float
    travel_date: str
    interests: List[str]

class RecommendedEvent(BaseModel):
    event_id: str
    name: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    match_score: float
