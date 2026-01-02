from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_project_root() -> Path:
    """获取项目根目录（即 backend 目录的父目录；动态向上查找 backend 目录）"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == 'backend':
            return parent.parent
    raise RuntimeError('未找到 backend 目录，无法确定项目根目录。')


class Settings(BaseSettings):
    """应用配置，支持从环境变量读取"""

    model_config = SettingsConfigDict(
        # 支持从多个位置读取 .env 文件：
        # 1. 项目根目录的 .env（优先）
        # 2. backend 目录的 .env（向后兼容）
        env_file=[
            str(_get_project_root() / '.env'),
        ],
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # 数据目录配置（唯一可配置的环境变量）
    # 默认使用项目根目录下的 data 文件夹
    # 在 Docker 中可以通过环境变量 DATA_DIR 覆盖
    data_dir: Path | None = Field(
        default=None,
        description='数据根目录路径',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保路径是绝对路径
        self._resolve_paths()

    def _resolve_paths(self) -> None:
        """解析路径，确保所有路径都是绝对路径"""
        # 如果没有设置 data_dir，使用默认值（项目根目录下的 data）
        if self.data_dir is None:
            self.data_dir = _get_project_root() / 'data'
        # 如果 data_dir 是相对路径，则相对于项目根目录
        elif not self.data_dir.is_absolute():
            project_root = _get_project_root()
            self.data_dir = (project_root / self.data_dir).resolve()
        else:
            self.data_dir = Path(self.data_dir).resolve()

    @property
    def books_dir(self) -> Path:
        """书籍存放目录（自动基于 data_dir 计算）"""
        return self.data_dir / 'books'

    @property
    def database_path(self) -> Path:
        """数据库文件路径（自动基于 data_dir 计算）"""
        return self.data_dir / 'database.db'

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
