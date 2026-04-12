from contextlib import contextmanager
from typing import Generator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, select
from sqlmodel import create_engine as create_sqlmodel_engine

from .config import settings
from .models import Meta
from .models import __version__ as MODEL_SCHEMA_VERSION

# 创建数据库引擎
# SQLite: check_same_thread=False 允许多线程各自持有 Session；timeout 为忙等秒数（缓解 database is locked）
_sqlite_connect_args = (
    {'check_same_thread': False, 'timeout': 30.0}
    if 'sqlite' in settings.database_url
    else {}
)

engine = create_sqlmodel_engine(
    settings.database_url,
    connect_args=_sqlite_connect_args,
    echo=False,  # 设置为 True 可以打印 SQL 语句（调试用）
)


@event.listens_for(engine, 'connect')
def _sqlite_wal_on_connect(dbapi_connection, _connection_record) -> None:
    """WAL 提升读写并发；busy_timeout 与 connect timeout 叠加，降低锁冲突概率。"""
    if engine.dialect.name != 'sqlite':
        return
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.execute('PRAGMA busy_timeout=30000')
    cursor.close()


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
