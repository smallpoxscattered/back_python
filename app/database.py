from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# 替换以下数据库配置
DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/LSZ"

engine = create_engine(DATABASE_URI)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
