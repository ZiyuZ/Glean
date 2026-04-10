from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, select
from sqlmodel import create_engine as create_sqlmodel_engine

from .config import settings
from .models import Meta
from .models import __version__ as MODEL_SCHEMA_VERSION

# 创建数据库引擎
# SQLite 需要 check_same_thread=False 以支持多线程
# 使用 connect_args 配置 SQLite 连接参数
engine = create_sqlmodel_engine(
    settings.database_url,
    connect_args={'check_same_thread': False} if 'sqlite' in settings.database_url else {},
    echo=False,  # 设置为 True 可以打印 SQL 语句（调试用）
)


def init_db() -> None:
    """初始化数据库，创建所有表并校验 schema_version。"""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        schema_meta = session.exec(select(Meta).where(Meta.key == 'schema_version')).first()
        if not schema_meta:
            session.add(Meta(key='schema_version', value=MODEL_SCHEMA_VERSION))
            session.commit()
            return
        if schema_meta.value != MODEL_SCHEMA_VERSION:
            raise RuntimeError(
                f'Database schema version mismatch: db={schema_meta.value}, '
                f'code={MODEL_SCHEMA_VERSION}. Please rebuild database before startup.'
            )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话的上下文管理器"""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：获取数据库会话"""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
