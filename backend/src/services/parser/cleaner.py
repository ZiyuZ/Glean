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
    i = 0
    while i < len(lines):
        line = lines[i]

        # 空行：保留（用于段落分隔）
        if not line:
            result_lines.append('')
            i += 1
            continue

        # 检查当前行是否应该合并下一行
        # 条件：行尾没有标点符号，且不太可能是标题行
        end_with_punctuation = line[-1] in end_punctuations
        is_likely_title = len(line) < max_title_length
        has_next_line = i + 1 < len(lines) and lines[i + 1]

        # 如果应该合并，且下一行存在且非空
        if not end_with_punctuation and not is_likely_title and has_next_line:
            # 合并下一行到当前行
            line += ' ' + lines[i + 1]
            i += 1
            # 继续检查合并后的行是否还需要继续合并
            continue

        # 不需要合并，直接添加
        result_lines.append(line)
        i += 1

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
