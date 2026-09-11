from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 定义数据库文件的名字
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 创建一个 Base 类，之后我们的模型会继承它
Base = declarative_base()
