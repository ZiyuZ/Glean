"""相似文件分析"""

import json
from dataclasses import asdict
from pathlib import Path

import torch
from config import SIMILARITY_FILE
from models import EmbeddingConfig, SimilarityConfig, SimilarityResult, SimilarPair


class SimilarityAnalyzer:
    """相似文件分析器"""

    def __init__(
        self,
        config: SimilarityConfig | None = None,
        embedding_config: EmbeddingConfig | None = None,
    ):
        self.config = config or SimilarityConfig()
        self.embedding_config = embedding_config or EmbeddingConfig()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._result: SimilarityResult | None = None

    def _aggregate_embedding(self, chunk_embeddings: torch.Tensor) -> torch.Tensor:
        """将块级嵌入平均为文档向量并归一化"""
        doc_emb = chunk_embeddings.mean(dim=0)
        return doc_emb / doc_emb.norm(p=2)

    def _compute_similarity_matrix(self, embeddings_list: list[torch.Tensor]) -> torch.Tensor:
        """向量化计算相似度矩阵"""
        mode = self.config.mode

        if mode == 'doc-mean':
            print('[Warning] doc-mean 模式下如 sample_count 过大可能产生偏高相似度')
            agg = torch.stack([self._aggregate_embedding(e) for e in embeddings_list])
            return torch.matmul(agg, agg.T)

        # chunk 级别向量化：堆叠成 (n_files, n_chunks, dim)
        stacked = torch.stack(embeddings_list)  # (n, k, d)

        # 对每个 chunk 位置计算所有文件间的相似度 -> (k, n, n)
        chunk_sims = torch.bmm(
            stacked.permute(1, 0, 2),  # (k, n, d)
            stacked.permute(1, 2, 0),  # (k, d, n)
        )

        if mode == 'chunk-max':
            return chunk_sims.max(dim=0).values
        elif mode == 'chunk-min':
            return chunk_sims.min(dim=0).values
        else:  # chunk-mean
            return chunk_sims.mean(dim=0)

    def analyze(self, embeddings: dict[str, torch.Tensor], debug: bool = False) -> SimilarityResult:
        """分析相似文件"""
        rel_paths = list(embeddings.keys())
        embeddings_list = [embeddings[p].to(self.device) for p in rel_paths]
        n = len(rel_paths)

        if debug:
            print(f'Files ({n}): {[Path(p).stem for p in rel_paths[:10]]}...')

        print(f'计算相似度矩阵，模式: {self.config.mode}...')
        matrix = self._compute_similarity_matrix(embeddings_list)

        if debug:
            print('Similarity matrix:\n', matrix.round(decimals=2))

        # 筛选相似对
        pairs: list[SimilarPair] = []
        for i in range(n):
            for j in range(i + 1, n):
                sim = matrix[i, j].item()
                if sim >= self.config.threshold:
                    pairs.append(
                        SimilarPair(
                            file1=rel_paths[i],
                            file2=rel_paths[j],
                            similarity=round(sim, 4),
                        )
                    )

        self._result = SimilarityResult(
            config=self.config,
            embedding_config=self.embedding_config,
            pairs=pairs,
        )

        print(f'找到 {len(pairs)} 对相似文件（阈值 >= {self.config.threshold}）')
        for p in pairs:
            print(f'  {p.similarity:.4f}: {Path(p.file1).name} <-> {Path(p.file2).name}')

        return self._result

    def save(self, output_file: Path = SIMILARITY_FILE) -> None:
        """保存分析结果"""
        if self._result is None:
            print('没有结果可保存，请先运行 analyze()')
            return

        data = asdict(self._result)
        output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'相似度分析结果已保存到 {output_file}')

    def load(self, input_file: Path = SIMILARITY_FILE) -> SimilarityResult | None:
        """加载分析结果"""
        if not input_file.exists():
            print(f'结果文件不存在: {input_file}')
            return None

        data = json.loads(input_file.read_text(encoding='utf-8'))
        self._result = SimilarityResult(
            config=SimilarityConfig(**data['config']),
            embedding_config=EmbeddingConfig(**data['embedding_config']),
            created_at=data['created_at'],
            pairs=[SimilarPair(**p) for p in data['pairs']],
        )
        print(f'已加载相似度分析结果，共 {len(self._result.pairs)} 对相似文件')
        return self._result

    @property
    def result(self) -> SimilarityResult | None:
        return self._result


if __name__ == '__main__':
    from embedder import Embedder
    from models import EmbeddingConfig, SimilarityConfig

    # 1. 加载嵌入
    emb_config = EmbeddingConfig(sample_count=4, chunk_size=512)
    embedder = Embedder(emb_config)
    embeddings = embedder.load()

    if not embeddings:
        print('请先运行 embedder.py 计算嵌入')
        exit(1)

    # 2. 分析相似文件
    sim_config = SimilarityConfig(mode='chunk-mean', threshold=0.9)
    analyzer = SimilarityAnalyzer(sim_config, emb_config)
    analyzer.analyze(embeddings, debug=True)
    analyzer.save()
