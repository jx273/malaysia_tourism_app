import csv
from sqlalchemy.orm import Session
from datetime import datetime

import crud
import schemas
from database import SessionLocal, engine
import models

def import_events(db: Session, file_path: str):
    print("\n--- 正在导入【精选活动】---")
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                try:
                    event_id = row['event_id']
                    if not event_id:
                        print("  -> !!! 错误 !!! 缺少 event_id，跳过此行。")
                        continue
                    
                    if crud.get_event_by_id(db, event_id=event_id):
                        print(f"  -> 活动 '{row['name']}' (ID: {event_id}) 已存在，跳过。")
                        continue

                    event_data = schemas.EventCreate(
                        event_id=row['event_id'],
                        name=row['name'],
                        description=row['description'],
                        category=row['category'],
                        address=row['address'],
                        latitude=float(row['latitude']) if row.get('latitude') else None,
                        longitude=float(row['longitude']) if row.get('longitude') else None,
                        start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row.get('start_date') else None,
                        end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row.get('end_date') else None,
                        opening_time=row['opening_time'],
                        closing_time=row['closing_time'],
                        price=row['price'],
                        image_url=row['image_url'],
                        recommendation_reason=row['recommendation_reason']
                    )
                    crud.create_event(db=db, event=event_data)
                    print(f"  -> 成功导入活动: {row['name']}")
                except Exception as e:
                    print(f"  -> !!! 错误 !!! 在处理活动 '{row.get('name', 'UNKNOWN')}' 时发生: {e}。跳过此行。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path} 文件，跳过活动导入。")


def import_state_stats(db: Session, file_path: str):
    print("\n--- 正在导入【州级统计数据】---")
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                try:
                    state, year = row['state'], row['year']
                    if not state or not year:
                        print("  -> !!! 错误 !!! 缺少 state 或 year，跳过此行。")
                        continue

                    if crud.get_state_stat(db, state=state, year=int(year)):
                        print(f"  -> 统计数据 '{state} ({year})' 已存在，跳过。")
                        continue
                    
                    stat_data = schemas.StateTourismStatsBase(
                        state=state,
                        year=int(year),
                        visitor_count=int(row['visitor_count']) if row.get('visitor_count') else None,
                        tourism_revenue=float(row['tourism_revenue']) if row.get('tourism_revenue') else None
                    )
                    crud.create_state_stat(db=db, stat=stat_data)
                    print(f"  -> 成功导入统计数据: {state} ({year})")
                except Exception as e:
                    print(f"  -> !!! 错误 !!! 在处理统计数据 '{row.get('state', 'UNKNOWN')}' 时发生: {e}。跳过此行。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path} 文件，跳过统计数据导入。")


def reset_database():
    print("\n--- 正在重置数据库 ---")
    models.Base.metadata.drop_all(bind=engine)
    print("  -> 所有旧表已删除。")
    models.Base.metadata.create_all(bind=engine)
    print("  -> 所有新表已创建。")

if __name__ == "__main__":
    db = SessionLocal()
    print("==========================================")
    print("       数据管理与导入脚本")
    print("==========================================")
    user_choice = input(
        "请选择操作:\n"
        "  1. 重置数据库并导入所有数据 (Reset & Import All)\n"
        "  2. 仅导入新数据 (Import New Data Only)\n"
        "  3. 退出 (Exit)\n"
        "请输入选项 (1/2/3): "
    )
    if user_choice == '1':
        reset_database()
        import_events(db, "events.csv")
        import_state_stats(db, "state_stats.csv")
        print("\n操作完成！")
    elif user_choice == '2':
        models.Base.metadata.create_all(bind=engine)
        import_events(db, "events.csv")
        import_state_stats(db, "state_stats.csv")
        print("\n操作完成！")
    else:
        print("\n已退出，未执行任何操作。")

    db.close()
