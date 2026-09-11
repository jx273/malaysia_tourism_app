from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

# 这是定义 "events" 这张表在数据库里真正拥有的所有列 (columns)
class Event(Base):
    __tablename__ = "events"

    # --- 核心字段 ---
    id = Column(Integer, primary_key=True, index=True) # 数据库自动生成的唯一 ID
    event_id = Column(String, unique=True, index=True) # 我们自己定义的活动 ID, e.g., "evt001"
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    # --- 详细信息字段 (v0.2 版本后添加) ---
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
