"""Retree 主入口 - 书库分析工具（使用 Typer CLI）"""

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer
from config import BOOKS_ROOT, RETREE_DATA
from models import EmbeddingConfig, SimilarityConfig, SimilarityMode
from scanner import MetadataManager

if TYPE_CHECKING:  # 避免导入 torch 影响启动速度
    from torch import Tensor

app = typer.Typer(
    name='retree',
    help='📚 书库文件分析工具 - 检测重复/相似文件',
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
)


# ============================================================
# 核心处理函数（供命令和 run 复用）
# ============================================================


def do_scan(books_root: Path = BOOKS_ROOT) -> MetadataManager:
    """扫描文件，返回 MetadataManager"""
    manager = MetadataManager(books_root=books_root)
    manager.scan()
    manager.save()
    return manager


def do_embed(
    rel_paths: list[str],
    config: EmbeddingConfig,
    force: bool = False,
) -> dict[str, 'Tensor']:
    """计算嵌入，返回 embeddings 字典

    只在需要计算时才导入 Embedder（延迟加载模型）
    """

    cache_file = RETREE_DATA / config.to_filename()

    # 检查是否需要计算
    if not force and cache_file.exists():
        import numpy as np  # noqa: PLC0415

        cached = np.load(cache_file, allow_pickle=True)
        cached_paths = set(cached.files)
        current_paths = set(rel_paths)

        # 如果缓存完全匹配，直接返回（不加载模型）
        if cached_paths == current_paths:
            import torch  # noqa: PLC0415

            print('嵌入缓存完全匹配，跳过计算')
            return {k: torch.from_numpy(cached[k]) for k in cached.files}

    # 需要计算，才导入 Embedder（加载模型）
    from embedder import Embedder  # noqa: PLC0415

    embedder = Embedder(config)

    if force:
        embedder.compute(rel_paths)
    else:
        embedder.load()
        embedder.sync(rel_paths)

    embedder.save()
    return embedder.embeddings


def do_similar(
    embeddings: dict[str, 'Tensor'],
    emb_config: EmbeddingConfig,
    sim_config: SimilarityConfig,
    debug: bool = False,
) -> None:
    """分析相似文件"""
    from similarity import SimilarityAnalyzer  # noqa: PLC0415

    analyzer = SimilarityAnalyzer(sim_config, emb_config)
    analyzer.analyze(embeddings, debug=debug)
    analyzer.save()


# ============================================================
# CLI 命令
# ============================================================


@app.command()
def scan(
    path: Annotated[
        Optional[Path],
        typer.Option('--path', '-p', help='书库路径（默认使用配置）'),
    ] = None,
) -> None:
    """扫描文件，收集元信息"""
    do_scan(path or BOOKS_ROOT)


@app.command()
def embed(
    sample_count: Annotated[int, typer.Option('--sample-count', '-s', help='采样块数')] = 4,
    chunk_size: Annotated[int, typer.Option('--chunk-size', '-c', help='块大小（字符）')] = 512,
    force: Annotated[bool, typer.Option('--force', '-f', help='强制全量重新计算')] = False,
) -> None:
    """计算文件嵌入向量（默认增量同步）"""
    manager = MetadataManager()
    metadata = manager.load()
    if not metadata:
        typer.echo('❌ 请先运行 scan 命令扫描文件', err=True)
        raise typer.Exit(1)

    config = EmbeddingConfig(sample_count=sample_count, chunk_size=chunk_size)
    do_embed(manager.list_paths(), config, force=force)


@app.command()
def similar(
    sample_count: Annotated[int, typer.Option('--sample-count', '-s', help='采样块数')] = 4,
    chunk_size: Annotated[int, typer.Option('--chunk-size', '-c', help='块大小')] = 512,
    mode: Annotated[
        SimilarityMode,
        typer.Option('--mode', '-m', help='相似度计算模式'),
    ] = 'chunk-mean',
    threshold: Annotated[float, typer.Option('--threshold', '-t', help='相似度阈值')] = 0.9,
    debug: Annotated[bool, typer.Option('--debug', help='调试模式')] = False,
) -> None:
    """分析相似文件"""
    from embedder import load_embeddings  # noqa: PLC0415

    emb_config = EmbeddingConfig(sample_count=sample_count, chunk_size=chunk_size)
    embeddings = load_embeddings(emb_config)

    if not embeddings:
        typer.echo('❌ 请先运行 embed 命令计算嵌入', err=True)
        raise typer.Exit(1)

    sim_config = SimilarityConfig(mode=mode, threshold=threshold)
    do_similar(embeddings, emb_config, sim_config, debug=debug)


@app.command()
def title(
    overwrite: Annotated[bool, typer.Option('--overwrite', help='覆盖已有的标准化标题')] = False,
) -> None:
    """运行标题标准化插件（需要 Ollama）"""
    from title_plugin import TitleStandardizer  # noqa: PLC0415

    manager = MetadataManager()
    metadata = manager.load()
    if not metadata:
        typer.echo('❌ 请先运行 scan 命令扫描文件', err=True)
        raise typer.Exit(1)

    standardizer = TitleStandardizer()
    standardizer.run(manager, overwrite=overwrite)
    manager.save()


@app.command(name='run')
def run_all(
    path: Annotated[
        Optional[Path],
        typer.Option('--path', '-p', help='书库路径（默认使用配置）'),
    ] = None,
    sample_count: Annotated[int, typer.Option('--sample-count', '-s', help='采样块数')] = 4,
    chunk_size: Annotated[int, typer.Option('--chunk-size', '-c', help='块大小')] = 512,
    mode: Annotated[
        SimilarityMode,
        typer.Option('--mode', '-m', help='相似度计算模式'),
    ] = 'chunk-mean',
    threshold: Annotated[float, typer.Option('--threshold', '-t', help='相似度阈值')] = 0.9,
    force: Annotated[bool, typer.Option('--force', '-f', help='强制重新计算嵌入')] = False,
    debug: Annotated[bool, typer.Option('--debug', help='调试模式')] = False,
) -> None:
    """执行完整流程: scan → embed → similar"""

    def _echo_step(text: str, separator: str = '=' * 50) -> None:
        typer.echo(f'\n{separator}')
        typer.echo(text)
        typer.echo(separator)

    typer.echo('📚 Retree 书库文件分析工具', nl=False)
    _echo_step('📁 步骤 1/3: 扫描文件')
    manager = do_scan(path or BOOKS_ROOT)

    _echo_step('🧮 步骤 2/3: 计算嵌入')
    emb_config = EmbeddingConfig(sample_count=sample_count, chunk_size=chunk_size)
    embeddings = do_embed(manager.list_paths(), emb_config, force=force)

    _echo_step('🔍 步骤 3/3: 分析相似文件')
    sim_config = SimilarityConfig(mode=mode, threshold=threshold)
    do_similar(embeddings, emb_config, sim_config, debug=debug)

    _echo_step('✅ 完成！')


@app.command()
def status() -> None:
    """查看当前数据状态"""
    import json  # noqa: PLC0415

    from config import METADATA_FILE, RETREE_DATA, SIMILARITY_FILE  # noqa: PLC0415

    typer.echo('📊 Retree 数据状态\n')

    # 元信息
    if METADATA_FILE.exists():
        data = json.loads(METADATA_FILE.read_text(encoding='utf-8'))
        typer.echo(f'📄 元信息: {len(data)} 个文件')
    else:
        typer.echo('📄 元信息: 未创建')

    # 嵌入缓存
    npz_files = list(RETREE_DATA.glob('embeddings_*.npz'))
    if npz_files:
        for f in npz_files:
            typer.echo(f'🧮 嵌入缓存: {f.name}')
    else:
        typer.echo('🧮 嵌入缓存: 未创建')

    # 相似度结果
    if SIMILARITY_FILE.exists():
        data = json.loads(SIMILARITY_FILE.read_text(encoding='utf-8'))
        typer.echo(f'🔍 相似度结果: {len(data.get("pairs", []))} 对相似文件')
    else:
        typer.echo('🔍 相似度结果: 未创建')


if __name__ == '__main__':
    app()
