import csv
from sqlalchemy.orm import Session
import os

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
                        continue
                    event_data = schemas.EventCreate(**row)
                    crud.create_event(db=db, event=event_data)
                except Exception:
                    continue
        print("  -> 【精选活动】导入完成。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path}，跳过活动导入。")

def import_state_stats(db: Session, file_path: str):
    print("\n--- 正在导入【最终州级统计和预测数据】---")
    try:
        db.query(models.StateTourismStats).delete()
        db.commit()
        print("  -> 已删除所有旧的州级统计数据。")

        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
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
                except Exception as e:
                    print(f"  -> !!! 错误 !!! 在处理行 {row.get('state')}-{row.get('year')} 时发生: {e}。跳过此行。")
        print(f"  -> 成功从 {file_path} 导入数据。")
    except FileNotFoundError:
        print(f"  -> 警告: 未找到 {file_path}。")

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
    print("自动执行：重置数据库并导入所有数据。")
    reset_database()
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    events_file = os.path.join(backend_dir, 'events.csv')
    predictions_file = os.path.join(project_root, 'ml', 'handoff', 'for_hongyik', 'sample_predictions.csv')
    import_events(db, events_file)
    import_state_stats(db, predictions_file)
    print("\n操作完成！")
    db.close()
