"""Embedding 计算与缓存"""

import re
from pathlib import Path

import chardet
import numpy as np
import torch
from config import BOOKS_ROOT, RETREE_DATA
from models import EmbeddingConfig
from opencc import OpenCC
from rich.progress import track


def load_embeddings(config: EmbeddingConfig | None = None) -> dict[str, torch.Tensor]:
    """从 npz 文件加载嵌入（不加载模型）

    Args:
        config: 嵌入配置，用于确定缓存文件名

    Returns:
        rel_path -> Tensor 的字典，如果文件不存在返回空字典
    """
    config = config or EmbeddingConfig()
    cache_file = RETREE_DATA / config.to_filename()

    if not cache_file.exists():
        print(f'缓存文件不存在: {cache_file}')
        return {}

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    data = np.load(cache_file, allow_pickle=True)
    embeddings = {k: torch.from_numpy(data[k]).to(device) for k in data.files}
    print(f'已加载 {len(embeddings)} 个文件的嵌入（设备: {device}）')
    return embeddings


class Embedder:
    """文档嵌入计算与缓存"""

    def __init__(self, config: EmbeddingConfig | None = None, books_root: Path = BOOKS_ROOT):
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415

        self.config = config or EmbeddingConfig()
        self.books_root = books_root
        self.cache_file = RETREE_DATA / self.config.to_filename()

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'使用设备: {self.device}, 加载模型: {self.config.model_name}...')
        self.model = SentenceTransformer(self.config.model_name, device=self.device)
        print('模型加载完成。')

        self._converter = OpenCC('t2s')
        self._embeddings: dict[str, torch.Tensor] = {}  # rel_path -> Tensor

    def _extract_chunks(self, file_path: Path) -> list[str]:
        """从文件开头提取连续文本块"""
        with open(file_path, 'rb') as f:
            raw = f.read()

        detected = chardet.detect(raw)
        encoding = detected.get('encoding') or 'GB18030'
        content = raw.decode(encoding, errors='ignore')

        # 清洗：去除空白符 + 繁体转简体
        content = re.sub(r'\s+', '', content)
        content = str(self._converter.convert(content))

        chunks: list[str] = []
        for i in range(self.config.sample_count):
            start = i * self.config.chunk_size
            end = start + self.config.chunk_size
            chunk = content[start:end]
            if len(chunk) > 50:
                chunks.append(chunk)

        return chunks

    def _encode_file(self, file_path: Path) -> torch.Tensor:
        """计算单个文件的块级嵌入，返回 (num_chunks, dim)"""
        chunks = self._extract_chunks(file_path)
        embeddings = self.model.encode(
            chunks,
            convert_to_tensor=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings

    def compute(self, rel_paths: list[str]) -> dict[str, torch.Tensor]:
        """计算指定文件的嵌入（覆盖模式）"""
        print(f'计算 {len(rel_paths)} 个文件的嵌入...')
        self._embeddings.clear()

        for rel_path in track(rel_paths, description='计算嵌入'):
            file_path = self.books_root / rel_path
            if not file_path.exists():
                print(f'  [跳过] 文件不存在: {rel_path}')
                continue
            try:
                self._embeddings[rel_path] = self._encode_file(file_path)
            except Exception as e:
                print(f'  [失败] {rel_path}: {e}')

        return self._embeddings

    def sync(self, rel_paths: list[str]) -> dict[str, torch.Tensor]:
        """同步嵌入：只计算新增文件，删除不存在的文件

        Args:
            rel_paths: 当前有效的文件路径列表（来自 metadata）

        Returns:
            同步后的嵌入字典
        """
        current_set = set(rel_paths)
        cached_set = set(self._embeddings.keys())

        # 找出新增和删除的文件
        added = current_set - cached_set
        removed = cached_set - current_set

        if removed:
            print(f'移除 {len(removed)} 个已删除文件的嵌入')
            for rel_path in removed:
                del self._embeddings[rel_path]

        if added:
            print(f'计算 {len(added)} 个新增文件的嵌入...')
            for rel_path in track(list(added), description='计算新增嵌入'):
                file_path = self.books_root / rel_path
                if not file_path.exists():
                    continue
                try:
                    self._embeddings[rel_path] = self._encode_file(file_path)
                except Exception as e:
                    print(f'  [失败] {rel_path}: {e}')
        else:
            print('没有新增文件需要计算')

        return self._embeddings

    def save(self) -> None:
        """保存嵌入到 npz 文件"""
        if not self._embeddings:
            print('没有嵌入可保存')
            return

        # 转换为 numpy 保存
        data = {k: v.cpu().numpy() for k, v in self._embeddings.items()}
        np.savez_compressed(self.cache_file, **data)
        print(f'嵌入已保存到 {self.cache_file}')

    def load(self) -> dict[str, torch.Tensor]:
        """从 npz 文件加载嵌入"""
        self._embeddings = load_embeddings(self.config)
        return self._embeddings

    def get(self, rel_path: str) -> torch.Tensor | None:
        """获取单个文件的嵌入"""
        return self._embeddings.get(rel_path)

    def list_cached(self) -> list[str]:
        """返回已缓存的文件路径列表"""
        return list(self._embeddings.keys())

    @property
    def embeddings(self) -> dict[str, torch.Tensor]:
        return self._embeddings


if __name__ == '__main__':
    from scanner import MetadataManager

    # 1. 加载元信息
    manager = MetadataManager()
    manager.load()

    # 2. 计算嵌入
    config = EmbeddingConfig(sample_count=4, chunk_size=512)
    embedder = Embedder(config)
    embedder.compute(manager.list_paths())
    embedder.save()
