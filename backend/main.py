from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
import crud
from database import SessionLocal, engine

# --- 初始化 ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DOSM Datathon 2026 - Tourism App Backend",
    description="为柔佛旅游探索 App 和数据看板提供支持的 API",
    version="0.6.0", # 版本升级，因为我们增加了 UPDATE 功能！
)

# --- 依赖项 (Dependency) ---
def get_db():
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
    return {"message": "后端服务器 v0.6 已成功启动，已加入完整的 CRUD 功能！"}


# --- Dashboard 相关的核心接口 ---

@app.get("/dashboard/state-stats", response_model=List[schemas.StateTourismStats], tags=["Dashboard Core API"])
def get_all_state_tourism_stats(db: Session = Depends(get_db)):
    """【核心】获取所有州份的历年旅游统计数据。"""
    stats = db.query(models.StateTourismStats).all()
    return stats


# --- App 内容相关的接口 ---

@app.get("/app/events", response_model=List[schemas.Event], tags=["App Content (Events)"])
def read_events_for_app(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    """【为 App 服务】读取精选活动列表 (Read All)"""
    events = crud.get_events(db, skip=skip, limit=limit, search=search)
    return events

@app.get("/app/events/{event_id}", response_model=schemas.Event, tags=["App Content (Events)"])
def read_single_event_for_app(event_id: str, db: Session = Depends(get_db)):
    """【为 App 服务】获取单个精选活动 (Read One)"""
    db_event = crud.get_event_by_id(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@app.put("/app/events/{event_id}", response_model=schemas.Event, tags=["App Content (Events)"])
def update_event_for_app(event_id: str, event_update: schemas.EventUpdate, db: Session = Depends(get_db)):
    """【新】【为 App 服务】更新一个已存在的活动 (Update)"""
    db_event = crud.get_event_by_id(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return crud.update_event(db=db, db_event=db_event, event_update=event_update)


# --- 内部使用的接口 (从公开文档中隐藏) ---

@app.post("/internal/create-event", response_model=schemas.Event, include_in_schema=False)
def create_new_event_internal(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """【内部使用】创建一个新的“精选活动” (Create)"""
    db_event = crud.get_event_by_id(db, event_id=event.event_id)
    if db_event:
        raise HTTPException(status_code=400, detail="Event ID already registered")
    return crud.create_event(db=db, event=event)


# --- 已降级的 AI 接口 ---

@app.post("/legacy/recommend", response_model=List[schemas.RecommendedEvent], tags=["Legacy AI (Not Core)"])
def get_simple_recommendations(request: schemas.RecommendationRequest):
    """【旧版功能】基于规则的简单推荐。"""
    mock_recommendations = [
        {"event_id": "evt101", "name": "Pasar Karat JB", "match_score": 0.9},
        {"event_id": "evt102", "name": "Desaru Fruit Farm", "match_score": 0.8}
    ]
    return mock_recommendations
