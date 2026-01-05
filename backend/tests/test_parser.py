# pyright: reportMissingImports=false
import sys
from pathlib import Path
from typing import NamedTuple

# Add backend/src to path so we can import services
# Add backend/src to path so we can import services
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.parser import is_line_chapter_title


class Case(NamedTuple):
    text: str
    should_match: bool
    description: str


def test_chapter_regex_cases():
    test_cases = [
        # Positive Cases (Should Match)
        Case('第一章 开启', True, 'Standard Chapter'),
        Case('第1章开启', True, 'Standard Chapter'),
        Case('第100节 结束', True, 'Digit Chapter'),
        Case('   第一章    ', True, 'Whitespace prefix'),
        Case('###第一章 开始###', True, 'Symbol prefix/suffix'),
        Case('仙逆 第一章 开始', True, 'Book name prefix with space'),
        Case('1 开始', True, 'Number Prefix'),
        Case('1开始', True, 'Number Prefix'),
        Case('仙逆 1 开始', True, 'Book name prefix with space (number)'),
        Case('Chapter 1 Title', True, 'English Chapter'),
        Case('1. Introduction', True, 'Number dot'),
        # Negative Cases (Should NOT Match)
        Case('我们在第二节课后下楼，去学校门口买点东西。', False, 'False positive: Lesson'),
        Case('这是我第一回来吃这家店，味道比想象中好。', False, 'False positive: Time coming'),
        # Case('第一章已更新', False, "False positive: 'Already' suffix"), # 这种情况先忽略吧
        Case('前言', False, 'Non-chapter word'),
        Case(
            '前言这是特别长的一行所以这根本就不可能是标题因为它超过了三十个字'
            + '这样设计是为了避免匹配到正文中带有第一章开头的长句子',
            False,
            'Line Too Long',
        ),
        Case('这章很缓慢地码了5个小时，因为一直恶心想吐，难道怀孕了？', False, 'False positive: Lesson'),
        Case('"十七。"', False, 'Digit Chapter'),
        Case('T2……', False, 'Digit Chapter'),
        Case('1张月票换一章更新！', False, 'Keyword'),
        Case('3et专业手机电影下载', False, 'Keyword'),
    ]

    for case in test_cases:
        # Use is_line_chapter_title directly
        is_match = is_line_chapter_title(case.text)

        error_msg = (
            f"Failed: {case.description} - Text: '{case.text}'. Expected {case.should_match}, Got {is_match}"
        )
        assert is_match == case.should_match, error_msg
