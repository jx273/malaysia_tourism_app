from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

# --- 表 1: 为 App 提供内容的“精选活动”表 ---
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

# --- 表 2: 【新】为 Dashboard 提供核心分析数据的“州级统计”表 ---
class StateTourismStats(Base):
    __tablename__ = "state_tourism_stats"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    year = Column(Integer, index=True)
    visitor_count = Column(Integer, nullable=True)
    tourism_revenue = Column(Float, nullable=True)
    gdp = Column(Float, nullable=True)
    cpi = Column(Float, nullable=True)
    hotel_count = Column(Integer, nullable=True)
    # ... 我们可以根据 YiYu 最终的数据集，在这里添加更多列 ...
