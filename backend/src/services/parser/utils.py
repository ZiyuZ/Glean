import hashlib
from pathlib import Path

from chardet import detect
from loguru import logger


def detect_encoding(file_path: Path) -> str:
    """
    检测文件编码

    使用 chardet 检测文件编码
    返回编码名称（如 'utf-8', 'gb18030'）

    注意：charset-normalizer 在某些文件上可能返回 None，因此使用 chardet
    """
    # 读取前 1024 字节进行检测（对于大文件更高效）
    with open(file_path, 'rb') as f:
        sample = f.read(1024)

    result = detect(sample)
    encoding = result.get('encoding', None)
    # 如果检测失败，默认使用 gb18030（常见的中文编码）
    if not encoding:
        logger.warning(f'Failed to detect encoding for {file_path}, using default encoding gb18030')
        encoding = 'gb18030'
    # 统一处理 GB2312 -> GB18030
    if encoding.lower() == 'gb2312':
        encoding = 'gb18030'
    return encoding.lower()


def normalize_file(file_path: Path) -> None:
    """
    标准化文件：检测编码、解码、转换为 UTF-8 并保存

    只做编码转换，不清洗内容，保持原始内容不变
    """
    # 检测编码
    encoding = detect_encoding(file_path)

    # 读取并解码
    try:
        content_bytes = file_path.read_bytes()
        content = content_bytes.decode(encoding, errors='replace')
    except UnicodeDecodeError as e:
        logger.error(f'Failed to decode {file_path} with encoding {encoding}: {e}')
        raise

    # 转换为 UTF-8 并保存（覆盖原文件，但内容不变，只是编码转换）
    file_path.write_text(content, encoding='utf-8')
    if encoding != 'utf-8':
        logger.warning(f'Normalized file {file_path}: {encoding} -> utf-8')


def calculate_file_hash(file_path: Path) -> str:
    """
    计算文件内容的 MD5 哈希值

    用于检测文件是否被修改
    """
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        # 分块读取，避免大文件占用过多内存
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
