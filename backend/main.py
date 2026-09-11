from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 导入我们自己创建的模块
import models
import schemas
import crud
from database import SessionLocal, engine

# --- 初始化 ---

# 这行代码会告诉 SQLAlchemy 根据 models.py 的定义, 在数据库里创建所有表
# 如果表已经存在, 它不会重复创建
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="DOSM Datathon 2026 - Tourism App Backend",
    description="为柔佛旅游探索 App 提供数据支持的 API",
    version="0.4.0",
)


# ---------------------------------
#  依赖项 (Dependency)
# ---------------------------------
def get_db():
    """
    这个函数会被每个 API 接口调用。
    它会创建一个数据库连接 (Session)，并在 API 请求处理完成后自动关闭它。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------
#  API 接口 (Endpoints)
# ---------------------------------

@app.get("/")
def read_root():
    """
    根路径，用于测试服务器是否正常运行。
    """
    return {"message": "后端服务器 v0.4 已成功启动！"}


# --- 活动 (Events) 相关的接口 ---

@app.post("/events/", response_model=schemas.Event, tags=["Events"])
def create_new_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    创建一个新的活动 (Event)。
    
    - **event_id**: 活动的唯一 ID (例如 "evt001")
    - **name**: 活动名称
    - **description**: 活动的详细描述 (可选)
    """
    # 检查 event_id 是否已经在数据库中存在
    db_event = crud.get_event_by_id(db, event_id=event.event_id)
    if db_event:
        raise HTTPException(status_code=400, detail="Event ID already registered")
    
    # 调用 crud.py 里的函数来创建并保存到数据库
    return crud.create_event(db=db, event=event)


@app.get("/events/", response_model=List[schemas.Event], tags=["Events"])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    读取活动列表，支持分页。
    
    - **skip**: 跳过前 N 条记录
    - **limit**: 最多返回 N 条记录
    """
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@app.get("/events/{event_id}", response_model=schemas.Event, tags=["Events"])
def read_event(event_id: str, db: Session = Depends(get_db)):
    """
    通过 event_id 获取单个活动的详细信息。
    """
    db_event = crud.get_event_by_id(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


# --- AI 推荐相关的接口 ---

@app.post("/recommend", response_model=List[schemas.RecommendedEvent], tags=["AI Recommendation"])
def get_recommendations(request: schemas.RecommendationRequest):
    """
    接收用户的偏好，返回 AI 推荐的活动结果。
    
    - **lat/lng**: 用户当前位置
    - **travel_date**: 用户的旅行日期
    - **interests**: 用户的兴趣标签列表 (例如 ["culture", "food"])
    """
    print(f"收到推荐请求: {request.dict()}")

    # --- 假的 AI 推荐逻辑 (之后这里会调用 YiYu 的模型) ---
    # 目前我们直接返回一个硬编码的假结果，方便 JiaXuan 开发界面
    mock_recommendations = [
        {
            "event_id": "evt001",
            "name": "柔佛古庙游神",
            "category": "Cultural",
            "image_url": "https://example.com/chingay.jpg",
            "match_score": 0.94
        },
        {
            "event_id": "evt002",
            "name": "新山乐高乐园",
            "category": "Theme Park",
            "image_url": "https://example.com/legoland.jpg",
            "match_score": 0.82
        }
    ]
    return mock_recommendations

