import re
from html.parser import HTMLParser
from typing import override

from opencc_purepy import OpenCC

# Maximimum title length for checking during line break cleaning
MAX_TITLE_LENGTH_FOR_CLEANING = 15
# Punctuation that likely indicates end of a sentence/line
END_PUNCTUATIONS = '。？！；）》〉】』」﹄〕…—～﹏￥'

_FULL_TO_HALF_TRANS = str.maketrans(
    '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ「」',
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""',
)


def clean_html(content: str) -> str:
    """
    去除 HTML 标签，提取纯文本
    """

    class HTMLTextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.result: list[str] = []

        @override
        def handle_data(self, data: str):
            self.result.append(data)

        def get_text(self) -> str:
            return ''.join(self.result)

    parser = HTMLTextExtractor()
    parser.feed(content)
    return parser.get_text()


def clean_line_breaks(
    content: str,
    # 最大标题长度
    max_title_length: int = MAX_TITLE_LENGTH_FOR_CLEANING,
    # 可能的行末标点符号
    end_punctuations: str = END_PUNCTUATIONS,
) -> str:
    """
    清理多余的换行符

    处理逻辑：
    1. 合并连续换行：连续多个换行合并为一个换行（段落分隔）
    2. 恢复被拆分的句子：如果行尾不是标点符号，且不太可能是标题，则合并下一行

    这是因为网站按宽度拆分文本，导致原本一个句子被分成多行，需要恢复。
    """
    # 合并连续的多个换行（保留一个，用于段落分隔）
    content = re.sub(r'(?:\r\n|\r|\n){3,}', '\n', content)

    # 按行处理，恢复被拆分的句子
    lines = [line.strip() for line in content.split('\n')]
    if not lines:
        return content

    result_lines = []
    buffer = []
    buffer_len = 0

    for line in lines:
        # 空行：先刷新缓冲区，但不添加空行到结果中
        if not line:
            if buffer:
                result_lines.append(' '.join(buffer))
                buffer = []
                buffer_len = 0
            continue

        # 将当前行加入缓冲区（相当于通过栈积累碎片）
        buffer.append(line)
        buffer_len += len(line)

        # 检查是否因为标点或标题原因，当前缓冲区内容已经构成完整的一段/句
        # 条件：行尾是标点符号，或者总长度像是标题
        end_with_punctuation = line[-1] in end_punctuations

        # 计算当前合并后的总长度：字符长度 + 空格数量
        current_total_len = buffer_len + max(0, len(buffer) - 1)
        is_likely_title = current_total_len < max_title_length

        if end_with_punctuation or is_likely_title:
            # 缓冲区内容已完整，刷新到结果
            result_lines.append(' '.join(buffer))
            buffer = []
            buffer_len = 0

    # 处理剩余的缓冲区内容
    if buffer:
        result_lines.append(' '.join(buffer))

    # 重新组合，段落之间用两个换行分隔
    return '\n\n'.join(result_lines)


def clean_content(content: str) -> str:
    """
    清洗文本内容

    执行以下清洗步骤：
    1. 去除 HTML 标签
    2. 全角转半角（数字、字母、引号）
    3. 繁体转简体
    4. 清理多余换行
    """
    # 1. 去除 HTML 标签
    content = clean_html(content)

    # 2. 全角转半角
    content = content.translate(_FULL_TO_HALF_TRANS)

    # 3. 繁体转简体
    converter = OpenCC('t2s')
    content = converter.convert(content)

    # 4. 清理多余换行
    content = clean_line_breaks(content)

    return content
