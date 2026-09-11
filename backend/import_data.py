import csv
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal

def import_data_from_csv(db: Session, file_path: str):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            print(f"正在导入: {row['name']}")
            
            # 检查数据是否已存在
            db_event = crud.get_event_by_id(db, event_id=row['event_id'])
            if db_event:
                print(f"  -> ID {row['event_id']} 已存在，跳过。")
                continue

            # 创建 Pydantic schema 对象
            event_data = schemas.EventCreate(
                event_id=row['event_id'],
                name=row['name'],
                description=row.get('description'),
                category=row.get('category'),
                price=row.get('price')
                # ... 可以添加所有其他字段
            )
            
            # 调用你的 crud 函数来创建数据
            crud.create_event(db=db, event=event_data)
            print(f"  -> {row['name']} 成功导入！")

if __name__ == "__main__":
    print("开始批量导入数据...")
    db = SessionLocal()
    try:
        # 假设 CSV 文件就在同一个文件夹里
        import_data_from_csv(db, file_path="events.csv")
        print("数据导入完成！")
    finally:
        db.close()
