from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# ---------------------------------
#  Pydantic 模型 (Schemas)
# ---------------------------------
#  - 这些模型定义了 API 的数据应该是什么样子
#  - 它们与数据库模型 (models.py) 是分开的
# ---------------------------------


# --- Event Schemas ---

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
    """
    【这就是之前缺失的模型】
    在创建新 Event 时，API 请求体 (Request Body) 需要遵循这个格式。
    它继承了 EventBase 的所有字段。
    """
    pass # Pass 意味着它和 EventBase 有完全相同的字段


class Event(EventBase):
    """
    在从 API 读取/返回 Event 数据时，遵循这个格式。
    它增加了数据库自动生成的 'id' 字段。
    """
    id: int
    
    # Pydantic v2 的配置, 替代了 orm_mode
    model_config = ConfigDict(from_attributes=True)


# --- Recommendation Schemas ---

class RecommendationRequest(BaseModel):
    """AI 推荐接口的请求格式"""
    lat: float
    lng: float
    travel_date: str
    interests: List[str]


class RecommendedEvent(BaseModel):
    """AI 推荐接口的返回格式"""
    event_id: str
    name: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    match_score: float

