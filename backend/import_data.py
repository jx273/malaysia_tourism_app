import csv
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal, engine # <--- 导入 engine
import models                           # <--- 导入 models
from datetime import datetime

def import_data_from_csv(db: Session, file_path: str):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print(f"正在导入: {row['name']}")
            
            db_event = crud.get_event_by_id(db, event_id=row['event_id'])
            if db_event:
                print(f"  -> ID {row['event_id']} 已存在，跳过。")
                continue

            start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row.get('start_date') else None
            end_date = datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row.get('end_date') else None

            event_data = schemas.EventCreate(
                event_id=row['event_id'],
                name=row['name'],
                description=row.get('description'),
                category=row.get('category'),
                address=row.get('address'),
                latitude=float(row['latitude']) if row.get('latitude') else None,
                longitude=float(row['longitude']) if row.get('longitude') else None,
                start_date=start_date,
                end_date=end_date,
                opening_time=row.get('opening_time'),
                closing_time=row.get('closing_time'),
                price=row.get('price'),
                image_url=row.get('image_url'),
                recommendation_reason=row.get('recommendation_reason')
            )
            
            crud.create_event(db=db, event=event_data)
            print(f"  -> {row['name']} 成功导入！")

if __name__ == "__main__":
    print("开始批量导入数据...")
    
    # --- 【这是新增的关键步骤】 ---
    # 在进行任何操作之前，先确保数据库和表已经被创建
    print("正在创建数据库表 (如果不存在)...")
    models.Base.metadata.create_all(bind=engine)
    print("数据库表已准备就绪。")
    # --------------------------------

    db = SessionLocal()
    try:
        import_data_from_csv(db, file_path="events.csv")
        print("数据导入完成！")
    finally:
        db.close()

