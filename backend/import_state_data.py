import csv
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal, engine
import models

def import_state_data_from_csv(db: Session, file_path: str):
    """
    从 CSV 文件读取州级统计数据，并将其导入数据库。
    """
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            state = row['state']
            year = int(row['year'])
            print(f"正在处理: {state} - {year}")
            
            # 1. 检查这条数据是否已经存在
            db_stat = crud.get_state_stat(db, state=state, year=year)
            if db_stat:
                print(f"  -> 数据已存在，跳过。")
                continue

            # 2. 准备数据，并转换为正确的类型
            try:
                stat_data = schemas.StateTourismStatsBase(
                    state=state,
                    year=year,
                    visitor_count=int(row['visitor_count']) if row.get('visitor_count') else None,
                    tourism_revenue=float(row['tourism_revenue']) if row.get('tourism_revenue') else None,
                )
            except (ValueError, TypeError) as e:
                print(f"  -> !!! 数据格式错误: {e}。跳过此行。")
                continue

            # 3. 调用 crud 函数来创建数据
            crud.create_state_stat(db=db, stat=stat_data)
            print(f"  -> {state} ({year}) 成功导入！")

if __name__ == "__main__":
    print("--- 开始批量导入【州级统计数据】---")
    
    # 确保数据库和所有表都已创建
    print("正在创建数据库表 (如果不存在)...")
    models.Base.metadata.create_all(bind=engine)
    print("数据库表已准备就绪。")
    
    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 运行导入函数
        import_state_data_from_csv(db, file_path="state_stats.csv")
        print("--- 【州级统计数据】导入完成！---")
    finally:
        # 确保最后关闭会话
        db.close()
