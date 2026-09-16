import csv
from sqlalchemy.orm import Session
from datetime import datetime
import os

import crud
import schemas
from database import SessionLocal, engine
import models

# (The import_events function remains the same)
def import_events(db: Session, file_path: str):
    print("\n--- 正在导入【精选活动】---")
    # ... (code is unchanged)

def import_state_stats(db: Session, file_path: str):
    print("\n--- 正在导入【最终州级统计和预测数据】---")
    try:
        # First, delete all old stats to make way for the new master data
        db.query(models.StateTourismStats).delete()
        db.commit()
        print("  -> 已删除所有旧的州级统计数据。")

        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                try:
                    # Convert boolean string to actual boolean
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
        print(f"  -> 警告: 未找到 {file_path}。请确保你已经切换到 feature/data-ai 分支并从根目录运行。")

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
        "  2. 退出 (Exit)\n"
        "请输入选项 (1/2): "
    )
    if user_choice == '1':
        reset_database()
        # Note: We run this from the backend/ directory, so we go up one level
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        predictions_file = os.path.join(project_root, 'ml', 'handoff', 'for_hongyik', 'sample_predictions.csv')
        
        import_events(db, "events.csv")
        import_state_stats(db, predictions_file)
        print("\n操作完成！")
    else:
        print("\n已退出，未执行任何操作。")

    db.close()
