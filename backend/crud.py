from sqlalchemy.orm import Session
import models
import schemas

# ---------------------------------
#  读取 (Read) 操作
# ---------------------------------

def get_event_by_id(db: Session, event_id: str):
    """
    通过 event_id (例如 "evt001") 从数据库中查询单个活动。
    """
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100):
    """
    从数据库中查询活动列表，支持分页。
    """
    return db.query(models.Event).offset(skip).limit(limit).all()


# ---------------------------------
#  创建 (Create) 操作
# ---------------------------------

def create_event(db: Session, event: schemas.EventCreate):
    """
    在数据库中创建一个新的 Event。
    这个函数会把所有从 API 接收到的字段都保存到数据库里。
    """
    
    # 根据 schemas.EventCreate 的数据, 创建一个 SQLAlchemy 的 models.Event 对象
    db_event = models.Event(
        # --- 核心信息 ---
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        
        # --- 详细信息 (从 v0.2 版本开始) ---
        # 我们在这里假设 EventCreate schema 也会包含这些字段
        # 如果 schemas.py 里的 EventCreate 没有这些字段, 需要去那边加上
        category=getattr(event, 'category', None),
        address=getattr(event, 'address', None),
        latitude=getattr(event, 'latitude', None),
        longitude=getattr(event, 'longitude', None),
        start_date=getattr(event, 'start_date', None),
        end_date=getattr(event, 'end_date', None),
        opening_time=getattr(event, 'opening_time', None),
        closing_time=getattr(event, 'closing_time', None),
        price=getattr(event, 'price', None),
        image_url=getattr(event, 'image_url', None),
        recommendation_reason=getattr(event, 'recommendation_reason', None)
    )
    
    db.add(db_event)      # 1. 将新创建的对象添加到数据库会话 (Session)
    db.commit()           # 2. 提交事务，将所有更改（包括添加）真正写入到数据库文件
    db.refresh(db_event)  # 3. 刷新对象，这样 db_event 就会包含从数据库中新获取的信息 (比如自动生成的 id)
    
    return db_event

# ---------------------------------
#  更新 (Update) 和删除 (Delete) 操作 (未来可以添加)
# ---------------------------------
# def update_event(...):
#     pass

# def delete_event(...):
#     pass
