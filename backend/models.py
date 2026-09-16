from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from database import Base

# --- Table 1: App Content (Events) ---
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    opening_time = Column(String, nullable=True)
    closing_time = Column(String, nullable=True)
    price = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    recommendation_reason = Column(String, nullable=True)

# --- Table 2: Dashboard Core Data (Final Version) ---
class StateTourismStats(Base):
    __tablename__ = "state_tourism_stats"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    year = Column(Integer, index=True)

    # Columns from the final predictions.csv
    visitors_000 = Column(Float, nullable=True)
    expected_visitors_000 = Column(Float, nullable=True)
    actual_share_pct = Column(Float, nullable=True)
    expected_share_pct = Column(Float, nullable=True)
    opportunity_gap_pp = Column(Float, nullable=True)
    opportunity_gap_pct = Column(Float, nullable=True)
    is_holdout_year = Column(Boolean, nullable=True)
    naive_forecast_next_year_000 = Column(Float, nullable=True)
