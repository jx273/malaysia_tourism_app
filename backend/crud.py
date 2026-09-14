from sqlalchemy.orm import Session
import models
import schemas

# ---------------------------------
#  Event CRUD Functions
# ---------------------------------

def get_event_by_id(db: Session, event_id: str):
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()

def get_events(db: Session, skip: int = 0, limit: int = 100, search: str = ""):
    query = db.query(models.Event)
    if search:
        query = query.filter(models.Event.name.contains(search))
    return query.offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# ---------------------------------
#  State Tourism Stats CRUD Functions (新功能!)
# ---------------------------------

def get_state_stat(db: Session, state: str, year: int):
    """【新】通过州和年份查询单条统计记录，用于检查重复。"""
    return db.query(models.StateTourismStats).filter(
        models.StateTourismStats.state == state,
        models.StateTourismStats.year == year
    ).first()

def create_state_stat(db: Session, stat: schemas.StateTourismStatsBase):
    """【新】在数据库中创建一条新的州级统计数据。"""
    # 使用 .model_dump() 可以更简洁地传递所有字段
    db_stat = models.StateTourismStats(**stat.model_dump())
    db.add(db_stat)
    db.commit()
    db.refresh(db_stat)
    return db_stat
