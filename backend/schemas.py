from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# ---------------------------------
#  Pydantic Schemas - 定义 API 数据的形状
# ---------------------------------

# --- App 内容 (Events) 相关的 Schemas ---

class EventBase(BaseModel):
    """所有 Event 模型共享的基础字段"""
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
    """创建新 Event 时，API 请求体需要遵循的格式"""
    pass

class Event(EventBase):
    """从 API 读取/返回 Event 数据时遵循的格式"""
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Dashboard 核心 API 相关的 Schemas ---

class StateTourismStatsBase(BaseModel):
    """所有州级统计数据共享的基础字段"""
    state: str
    year: int
    visitor_count: Optional[int] = None
    tourism_revenue: Optional[float] = None
    gdp: Optional[float] = None
    cpi: Optional[float] = None
    hotel_count: Optional[int] = None

class StateTourismStats(StateTourismStatsBase):
    """从 API 读取/返回州级统计数据时遵循的格式"""
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- 旧版 AI 推荐相关的 Schemas ---

class RecommendationRequest(BaseModel):
    """旧版推荐接口的请求格式"""
    lat: float
    lng: float
    travel_date: str
    interests: List[str]

class RecommendedEvent(BaseModel):
    """旧版推荐接口的返回格式"""
    event_id: str
    name: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    match_score: float
