from sqlmodel import SQLModel, create_engine, Session
# SQLModel 管理所有表模型
# create_engine 创建数据库连接引擎
# Session 创建一次数据库会话。


DATABASE_URL = "sqlite:///./mini_kb.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  #打印SQL日志
    connect_args={"check_same_thread": False}, #SQLite 默认要求：创建数据库连接的线程，和使用数据库连接的线程必须是同一个线程。
)


def create_db_and_tables():
    # 找到所有继承了 SQLModel且table = True的模型，然后在数据库里创建对应的数据表。
    SQLModel.metadata.create_all(engine)


#每次请求接口时，创建一个数据库会话；请求结束后，自动关闭会话。
def get_session():
    with Session(engine) as session:
        yield session