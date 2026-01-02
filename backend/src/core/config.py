from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_project_root() -> Path:
    """获取项目根目录（backend 的父目录）"""
    # 从 backend/src/core/config.py 向上找到项目根目录
    return Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    """应用配置，支持从环境变量读取"""

    model_config = SettingsConfigDict(
        # 支持从多个位置读取 .env 文件：
        # 1. 项目根目录的 .env（优先）
        # 2. backend 目录的 .env（向后兼容）
        env_file=[
            str(_get_project_root() / '.env'),
            '.env',  # 相对路径，从当前工作目录查找
        ],
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # 数据目录配置
    # 默认使用项目根目录下的 data 文件夹
    # 在 Docker 中可以通过环境变量 DATA_DIR 覆盖
    data_dir: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / 'data',
        description='数据根目录路径',
    )

    # 书籍目录（相对于 data_dir 或绝对路径）
    books_dir: Path = Field(
        default=Path('books'),
        description='书籍存放目录',
    )

    # 数据库文件路径（相对于 data_dir 或绝对路径）
    database_path: Path = Field(
        default=Path('database.db'),
        description='SQLite 数据库文件路径',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保路径是绝对路径
        self._resolve_paths()

    def _resolve_paths(self) -> None:
        """解析路径，确保所有路径都是绝对路径"""
        # 如果 data_dir 是相对路径，则相对于项目根目录
        if not self.data_dir.is_absolute():
            # 从 backend/src/core/config.py 向上找到项目根目录
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = (project_root / self.data_dir).resolve()
        else:
            self.data_dir = self.data_dir.resolve()

        # 解析 books_dir
        if not self.books_dir.is_absolute():
            self.books_dir = (self.data_dir / self.books_dir).resolve()
        else:
            self.books_dir = self.books_dir.resolve()

        # 解析 database_path
        if not self.database_path.is_absolute():
            self.database_path = (self.data_dir / self.database_path).resolve()
        else:
            self.database_path = self.database_path.resolve()

    @property
    def database_url(self) -> str:
        """返回 SQLite 数据库连接 URL"""
        return f'sqlite:///{self.database_path}'

    def ensure_directories(self) -> None:
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.books_dir.mkdir(parents=True, exist_ok=True)
        # 数据库文件所在的目录
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
