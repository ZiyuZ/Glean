import re

# --- 基础子模式 ---
# 中文数字: 一到七位 (如: 一千七百二十一)
_CHINESE_NUM = r'[一二三四五六七八九十百千万]{1,7}'
# 阿拉伯数字: 1-4位，且后面不能直接跟着数字（防止匹配长数字的前几位）
_DIGIT_NUM = r'\d{1,4}(?!\d)'
# 统称数字模式
_ANY_NUM = rf'({_CHINESE_NUM}|{_DIGIT_NUM})'

# 特殊章节关键词
_SPECIAL_WORDS = r'(序[言]?|前言|自序|楔子|引子|导言|后记|完本感言|结语|尾声|终章|番外|外传|附录)'


def _generate_chapter_regex() -> re.Pattern[str]:
    """
    获取章节标题匹配的正则表达式（宽松模式）
    """
    patterns = [
        # 1. 标准中文章节: 第1章, 第一百二十章, 第12回
        rf'第{_ANY_NUM}[章节回]',
        # 2. 纯数字/序号模式: "1. 简介", "101 标题"
        # 要求前面没有汉字或字母相连，防止误匹配 "T2", "第一"
        rf'(?<![\u4e00-\u9fff]|[A-Za-z\d]){_DIGIT_NUM}',
        # 3. 分卷模式: 分卷阅读1, 分卷阅读第一卷
        rf'分卷阅读{_ANY_NUM}',
        # 4. 目录关键词
        r'章节目录',
        # 5. 英文模式: Chapter 1
        rf'^Chapter\s+{_DIGIT_NUM}',
        # 6. 特殊关键词: 必须是行首，且后面跟着冒号、空格或是行尾
        rf'^{_SPECIAL_WORDS}([:：\s]|$)',
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

    # 2. 标点符号校验 (结尾不应该是逗号、顿号、冒号，且一般不包括句号)
    if line.endswith(('，', '、', '：')):
        return False
    if '。' in line:
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
    if match_end < len(line):
        suffix = line[match_end:].strip()
        # 如果是长度大于 20 且存在句号的很可能是句子
        if len(suffix) > 10 and '。' in suffix:
            return False

        # 如果长度太长一般也是正文
        if len(suffix) > 20:
            return False

    return True
