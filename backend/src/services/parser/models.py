import re
from dataclasses import dataclass

from .title_validator import is_line_chapter_title

END_PUNCTUATIONS = set(list('。！？；…』」」﹄—～》￥〕〉﹏】）".\'’”!?;'))


@dataclass(slots=True)
class BookLine:
    """
    一行原文。

    不缓存 ``kind`` 这类派生状态，统一通过方法按需判断，避免状态过期。
    """

    text: str

    def is_title(self) -> bool:
        return is_line_chapter_title(self.text)

    def normalized_title(self) -> str:
        """章节标题入库用：仅保留汉字、字母数字与逗号空格，其余替换为空格后去首尾空白。"""
        return re.sub(r'[^\u4e00-\u9fffA-Za-z0-9， ]', ' ', self.text).strip()

    def is_end(self) -> bool:
        return bool(self.text) and self.text[-1] in END_PUNCTUATIONS

    def merge_with(self, other: BookLine) -> BookLine:
        return BookLine(f'{self.text}{other.text}')


@dataclass(slots=True)
class ParsedChapter:
    title: str
    body_lines: list[BookLine]

    def to_body(self) -> str:
        return '\n\n'.join(line.text for line in self.body_lines)
