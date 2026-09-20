import csv
import os
from datetime import datetime
from sqlalchemy.orm import Session

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
                    if crud.get_event_by_id(db, event_id=row['event_id']):
                        print(f"  -> ID {row['event_id']} 已存在，跳过。")
                        continue

                    # 安全解析日期（兼容空白情况）
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
                    print(f"  -> 成功导入: {row['name']}")
                except Exception as e:
                    print(f"  -> !!! 导入 {row.get('name')} 时出错: {e}")
                    
        print("  -> 【精选活动】导入完成。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path}，跳过活动导入。")

def import_state_stats(db: Session, file_path: str):
    print("\n--- 正在导入【最终州级统计和预测数据】---")
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            count = 0
            for row in csv_reader:
                try:
                    is_holdout = True if row.get('is_holdout_year', '').lower() == 'true' else False
                    stat_data = schemas.StateTourismStatsBase(
                        state=row.get('state'),
                        year=int(row['year']) if row.get('year') else None,
                        visitors_000=float(row['visitors_000']) if row.get('visitors_000') else None,
                        expected_visitors_000=float(row['expected_visitors_000']) if row.get('expected_visitors_000') else None,
                        actual_share_pct=float(row['actual_share_pct']) if row.get('actual_share_pct') else None,
                        expected_share_pct=float(row['expected_share_pct']) if row.get('expected_share_pct') else None,
                        opportunity_gap_pp=float(row['opportunity_gap_pp']) if row.get('opportunity_gap_pp') else None,
                        opportunity_gap_pct=float(row['opportunity_gap_pct']) if row.get('opportunity_gap_pct') else None,
                        is_holdout_year=is_holdout,
                        naive_forecast_next_year_000=float(row['naive_forecast_next_year_000']) if row.get('naive_forecast_next_year_000') else None
                    )
                    crud.create_state_stat(db=db, stat=stat_data)
                    count += 1
                except Exception as e:
                    print(f"  -> !!! 错误 !!! 在处理行 {row.get('state')}-{row.get('year')} 时发生: {e}。")
        print(f"  -> 成功从 {file_path} 导入了 {count} 条统计数据。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path}。")

def reset_database():
    print("\n--- 正在重置数据库 ---")
    models.Base.metadata.drop_all(bind=engine)
    print("  -> 所有旧表已彻底删除。")
    models.Base.metadata.create_all(bind=engine)
    print("  -> 所有新表已重新创建。")

if __name__ == "__main__":
    db = SessionLocal()
    print("==========================================")
    print("       LestariLens 数据管理与导入脚本")
    print("==========================================")
    
    # 1. 彻底重置数据库 (防止 String ID 和 Integer ID 冲突)
    reset_database()
    
    # 2. 动态获取路径
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    events_file = os.path.join(backend_dir, 'events.csv')
    predictions_file = os.path.join(project_root, 'ml', 'handoff', 'for_hongyik', 'sample_predictions.csv')
    
    # 3. 导入数据
    import_events(db, events_file)
    import_state_stats(db, predictions_file)
    
    print("\n✅ 所有数据库操作已顺利完成！")
    db.close()