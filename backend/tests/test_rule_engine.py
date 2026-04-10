import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.parser.models import LineRecord  # ty: ignore[unresolved-import]
from services.parser.rule_engine import RuleEngine  # ty: ignore[unresolved-import]


def _write_rules(rules_dir: Path, name: str, rules: list[dict]) -> None:
    payload = {'name': name, 'rules': rules}
    (rules_dir / f'{name}.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')


def test_rule_order_and_conflict_resolution(tmp_path: Path):
    rules_dir = tmp_path / 'rules'
    rules_dir.mkdir()
    _write_rules(
        rules_dir,
        '净化',
        [
            {
                'name': 'r1',
                'enabled': True,
                'regex': True,
                'pattern': 'abc',
                'replacement': 'x',
            },
            {
                'name': 'r2',
                'enabled': True,
                'regex': True,
                'pattern': 'x',
                'replacement': 'y',
            },
        ],
    )

    engine = RuleEngine(rules_dir=rules_dir)
    line = LineRecord(line_no=1, text='abc')
    hits = engine.apply_to_line(line)
    assert hits == 2
    assert line.text == 'y'


def test_invalid_regex_fails_fast_on_engine_init(tmp_path: Path):
    rules_dir = tmp_path / 'rules'
    rules_dir.mkdir()
    _write_rules(
        rules_dir,
        '净化',
        [
            {
                'name': 'disabled',
                'enabled': False,
                'regex': True,
                'pattern': 'foo',
                'replacement': 'bar',
            },
            {
                'name': 'invalid',
                'enabled': True,
                'regex': True,
                'pattern': '(',
                'replacement': '',
            },
        ],
    )
    with pytest.raises(ValueError, match='Invalid regex rule "invalid"'):
        RuleEngine(rules_dir=rules_dir)


def test_literal_rule_does_not_rerun_after_regex_change(tmp_path: Path):
    rules_dir = tmp_path / 'rules'
    rules_dir.mkdir()
    _write_rules(
        rules_dir,
        '净化',
        [
            {
                'name': 'regex_step',
                'enabled': True,
                'regex': True,
                'pattern': 'foo',
                'replacement': 'bar',
            },
            {
                'name': 'literal_step',
                'enabled': True,
                'regex': False,
                'pattern': 'bar',
                'replacement': 'baz',
            },
        ],
    )

    engine = RuleEngine(rules_dir=rules_dir)
    line = LineRecord(line_no=1, text='foo')
    hits = engine.apply_to_line(line)

    assert hits == 1
    assert line.text == 'bar'


def test_literal_then_regex_two_stage_pipeline(tmp_path: Path):
    rules_dir = tmp_path / 'rules'
    rules_dir.mkdir()
    _write_rules(
        rules_dir,
        '净化',
        [
            {
                'name': 'literal_first',
                'enabled': True,
                'regex': False,
                'pattern': 'foo',
                'replacement': 'bar',
            },
            {
                'name': 'regex_second',
                'enabled': True,
                'regex': True,
                'pattern': 'bar',
                'replacement': 'baz',
            },
        ],
    )

    engine = RuleEngine(rules_dir=rules_dir)
    line = LineRecord(line_no=1, text='foo')
    hits = engine.apply_to_line(line)

    assert hits == 2
    assert line.text == 'baz'
