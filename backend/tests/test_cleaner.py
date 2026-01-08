# pyright: reportMissingImports=false
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / 'src'))
from services.parser.cleaner import clean_line_breaks


@pytest.mark.parametrize(
    'content, expected, case_name',
    [
        (
            '这是一个很长的段落(80字)，它没有结束标点符号\n接下一行。',
            '这是一个很长的段落(80字)，它没有结束标点符号 接下一行。',
            'Split Paragraph',
        ),
        ('Chapter 1\nContent starts here.', 'Chapter 1\n\nContent starts here.', 'Title followed by content'),
        ('Para 1.\n\n\nPara 2.', 'Para 1.\n\nPara 2.', 'Empty lines'),
        (
            'Line 1 (no punc)\nLine 2 (no punc)\nLine 3 (punc).',
            'Line 1 (no punc) Line 2 (no punc) Line 3 (punc).',
            'Multi-line merge',
        ),
        ('Short\nNext line.', 'Short\n\nNext line.', 'Short line title heuristic'),
        ('', '', 'Empty Input'),
        (
            'Title\n\nPara 1 part 1 is definitely longer than fifteen characters.\nPara 1 part 2 is also longer to ensure merging.\n\nPara 2.',
            'Title\n\nPara 1 part 1 is definitely longer than fifteen characters. Para 1 part 2 is also longer to ensure merging.\n\nPara 2.',
            'Complex mix',
        ),
    ],
)
def test_clean_line_breaks(content: str, expected: str, case_name: str):
    """
    Test clean_line_breaks function with various scenarios.

    Args:
        content: Input string with messy line breaks
        expected: Expected output string with correct paragraph merging
        case_name: Description of the test case (used for debugging context)
    """
    result = clean_line_breaks(content)
    assert result == expected, f'Failed case: {case_name}'
