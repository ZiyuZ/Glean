import re


def _generate_chapter_regex() -> re.Pattern[str]:
    """
    获取章节标题匹配的正则表达式（宽松模式）
    """
    patterns = [
        # 中文章节
        r'第[一二三四五六七八九十百千万\d ]+[章节回]',
        # 纯数字匹配要求前面没有直接和汉字相连, 并且不超过5位数字
        r'(?<![\u4e00-\u9fff]|[A-Za-z])\d{1,5}',
        # 英文 Chapter
        r'^Chapter\s+\d+',
    ]
    combined_pattern = '|'.join(f'({pattern})' for pattern in patterns)
    return re.compile(combined_pattern, re.IGNORECASE | re.MULTILINE)


_CHAPTER_REGEX = _generate_chapter_regex()


def is_line_chapter_title(line: str) -> bool:
    """
    判断某一行是否为章节标题
    """
    line = line.strip()

    # 0. 基础过滤
    if not line:
        # 出现这种情况是有问题的, 空内容在前面就拦截掉了
        raise ValueError('Line is empty')

    # 1. 长度校验
    # 如果标题行太长（超过 30 字），极有可能不是标题而是正文
    if len(line) > 30:
        return False

    # 2. 标点符号校验 (结尾不应该是句号逗号)
    if line.endswith(('。', '，', ',', '.')):
        # 特例：如果有 "Chapter 1." 这种格式？
        # 一般来说中文小说标题不带句号
        return False

    # 3. 正则匹配
    match = _CHAPTER_REGEX.search(line)
    if not match:
        return False
    match_start = match.start()
    match_end = match.end()

    # 4. 前后缀校验
    # 允许有前缀（如书名），但长度不能超过 10, 且符合符号约束规则
    if match_start > 0:
        prefix = line[:match_start].strip()
        # 前缀太长（可能是正文）
        if len(prefix) > 10:
            return False
        # 前缀包含句读（可能是前一句的结束）
        if any(p in prefix for p in ('。', '，', ',', '.', ':', '：', '’', '”')):
            return False
    # 后缀通常是标题名, 长度不能超过 20, 且符合符号约束规则
    if match_end < len(line) - 1:
        suffix = line[match_end:].strip()
        # 如果是长度大于 20 且存在句号的很可能是句子
        if len(suffix) > 10 and '。' in suffix:
            return False

        # 如果长度太长一般也是正文
        if len(suffix) > 20:
            return False
    # 5. 语义校验
    # 过滤掉包含特定关键词的行，这些行通常是作者的话、求票或系统信息
    invalid_keywords = (
        '月票',
        '更新',
        '推荐票',
        '打赏',
        '订阅',
        '收藏',
        '加更',
        '完本',
        '感言',
        '上架',
        '章节目录',
        '目录',
        '求票',
        '谢谢',
        '感谢',
        '读者',
        '粉丝',
        '投个票',
        '投张',
        '投点',
        'QQ群',
        '下载',
    )
    if any(word in line for word in invalid_keywords):
        return False

    return True
