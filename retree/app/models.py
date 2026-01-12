"""数据模型定义"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

SimilarityMode = Literal['doc-mean', 'chunk-max', 'chunk-min', 'chunk-mean']


@dataclass
class FileMetadata:
    """文件元信息"""

    rel_path: str  # 相对于 BOOKS_ROOT 的路径
    size: int  # 文件大小（字节）
    modified_at: float  # 最后修改时间戳
    title: str = ''  # 原始文件名（不含扩展名）
    standardized_title: str = ''  # 标准化后的标题

    @classmethod
    def from_file(cls, file_path: Path, base_path: Path) -> 'FileMetadata':
        stat = file_path.stat()
        return cls(
            rel_path=str(file_path.relative_to(base_path)),
            size=stat.st_size,
            modified_at=stat.st_mtime,
            title=file_path.stem,
        )


@dataclass
class EmbeddingConfig:
    """Embedding 计算配置"""

    model_name: str = 'shibing624/text2vec-base-chinese'
    sample_count: int = 4
    chunk_size: int = 512

    def to_filename(self) -> str:
        """生成缓存文件名"""
        model_short = self.model_name.split('/')[-1]
        return f'embeddings_{model_short}_s{self.sample_count}_c{self.chunk_size}.npz'


@dataclass
class SimilarityConfig:
    """相似度分析配置"""

    mode: SimilarityMode = 'chunk-mean'
    threshold: float = 0.9


@dataclass
class SimilarPair:
    """相似文件对"""

    file1: str  # rel_path
    file2: str  # rel_path
    similarity: float


@dataclass
class SimilarityResult:
    """相似度分析结果"""

    config: SimilarityConfig
    embedding_config: EmbeddingConfig
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    pairs: list[SimilarPair] = field(default_factory=list)
