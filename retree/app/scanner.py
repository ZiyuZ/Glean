"""文件扫描与元信息管理"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from config import BOOKS_ROOT, METADATA_FILE, SUPPORTED_EXTENSIONS
from models import FileMetadata
from rich.progress import track


class MetadataManager:
    """文件元信息管理器"""

    def __init__(self, books_root: Path = BOOKS_ROOT, metadata_file: Path = METADATA_FILE):
        self.books_root = books_root
        self.metadata_file = metadata_file
        self._metadata: dict[str, FileMetadata] = {}  # rel_path -> FileMetadata

    def scan(self) -> dict[str, FileMetadata]:
        """扫描目录，收集所有文件元信息"""
        files = [
            f
            for f in self.books_root.rglob('*.*')
            if f.is_file() and f.stat().st_size > 0 and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        print(f'扫描到 {len(files)} 个文件...')

        self._metadata.clear()
        for file in track(files, description='收集元信息'):
            meta = FileMetadata.from_file(file, self.books_root)
            self._metadata[meta.rel_path] = meta

        return self._metadata

    def save(self) -> None:
        """保存元信息到文件"""
        data = {k: asdict(v) for k, v in self._metadata.items()}
        self.metadata_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'元信息已保存到 {self.metadata_file}')

    def load(self) -> dict[str, FileMetadata]:
        """从文件加载元信息"""
        if not self.metadata_file.exists():
            print(f'元信息文件不存在: {self.metadata_file}')
            return {}

        data = json.loads(self.metadata_file.read_text(encoding='utf-8'))
        self._metadata = {k: FileMetadata(**v) for k, v in data.items()}
        print(f'已加载 {len(self._metadata)} 条元信息')
        return self._metadata

    def get(self, rel_path: str) -> FileMetadata | None:
        """获取单个文件的元信息"""
        return self._metadata.get(rel_path)

    def update(self, rel_path: str, **kwargs: dict[str, Any]) -> None:
        """更新单个文件的元信息字段"""
        if rel_path in self._metadata:
            meta = self._metadata[rel_path]
            for k, v in kwargs.items():
                if hasattr(meta, k):
                    setattr(meta, k, v)

    def list_paths(self) -> list[str]:
        """返回所有文件的相对路径列表"""
        return list(self._metadata.keys())

    @property
    def metadata(self) -> dict[str, FileMetadata]:
        return self._metadata


if __name__ == '__main__':
    manager = MetadataManager()
    manager.scan()
    manager.save()
