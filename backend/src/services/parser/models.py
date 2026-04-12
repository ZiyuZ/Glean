import re
import unicodedata
from dataclasses import dataclass

from opencc_purepy import OpenCC

from .validator import is_line_chapter_title

_OPENCC = OpenCC('t2s')
_FULL_TO_HALF_TRANS = str.maketrans(
    '０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ「」',
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""',
)


@dataclass(slots=True)
class LineRecord:
    line_no: int
    text: str

    def __post_init__(self) -> None:
        """单行归一化：NFKC、全半角、繁简转换，并 strip 行首尾空白。"""
        normalized = unicodedata.normalize('NFKC', self.text).translate(_FULL_TO_HALF_TRANS)
        self.text = _OPENCC.convert(normalized).strip()
        if not self.text:
            raise ValueError('LineRecord text is empty after normalization')

    def is_title(self) -> bool:
        return is_line_chapter_title(self.text)

    def normalized_chapter_title(self) -> str:
        """章节标题入库用：仅保留汉字、字母数字与逗号空格，其余替换为空格后去首尾空白。"""
        return re.sub(r'[^\u4e00-\u9fffA-Za-z0-9， ]', ' ', self.text).strip()


@dataclass(slots=True)
class ParsedChapter:
    title: str
    body_lines: list[LineRecord]

    def to_body(self) -> str:
        return '\n\n'.join(line.text for line in self.body_lines if line.text)
