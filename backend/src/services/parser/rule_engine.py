import json
from pathlib import Path
from typing import Protocol, cast

import regex
from ahocorasick_rs import AhoCorasick
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from .models import LineRecord, ParsedChapter


def _focus_diff(before: str, after: str, context: int = 24) -> tuple[str, str]:
    """Return short before/after snippets around the first changed span."""
    if before == after:
        clip = before[: context * 2]
        suffix = '...' if len(before) > context * 2 else ''
        return f'{clip}{suffix}', f'{clip}{suffix}'

    prefix = 0
    shared_prefix = min(len(before), len(after))
    while prefix < shared_prefix and before[prefix] == after[prefix]:
        prefix += 1

    suffix = 0
    shared_suffix = min(len(before) - prefix, len(after) - prefix)
    while suffix < shared_suffix and before[-1 - suffix] == after[-1 - suffix]:
        suffix += 1

    before_change_end = len(before) - suffix if suffix else len(before)
    after_change_end = len(after) - suffix if suffix else len(after)
    window_start = max(prefix - context, 0)
    before_window_end = min(before_change_end + context, len(before))
    after_window_end = min(after_change_end + context, len(after))

    before_left = before[window_start:prefix]
    before_mid = before[prefix:before_change_end]
    before_right = before[before_change_end:before_window_end]
    after_left = after[window_start:prefix]
    after_mid = after[prefix:after_change_end]
    after_right = after[after_change_end:after_window_end]

    before_prefix = '...' if window_start > 0 else ''
    before_suffix = '...' if before_window_end < len(before) else ''
    after_prefix = '...' if window_start > 0 else ''
    after_suffix = '...' if after_window_end < len(after) else ''

    before_snippet = f'{before_prefix}{before_left}<<{before_mid}>>{before_right}{before_suffix}'
    after_snippet = f'{after_prefix}{after_left}<<{after_mid}>>{after_right}{after_suffix}'
    return before_snippet, after_snippet


class CompiledRegex(Protocol):
    def sub(self, replacement: str, value: str) -> str: ...


class RuleDefinition(BaseModel):
    name: str = Field(min_length=1)
    enabled: bool = True
    regex: bool = True
    pattern: str
    replacement: str

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('pattern cannot be blank')
        return value


class RuleFile(BaseModel):
    name: str
    rules: list[RuleDefinition] = Field(default_factory=list)

    def enabled_rules(self) -> list[RuleDefinition]:
        return [rule for rule in self.rules if rule.enabled]


class LiteralPatternMatcher:
    """Wrapper over ahocorasick_rs for literal (non-regex) rules."""

    def __init__(self, rules: list[RuleDefinition], debug: bool = False):
        self.debug = debug
        self._rules = rules
        self._automaton = AhoCorasick([rule.pattern for rule in rules if rule.pattern])

    def matched_patterns(self, text: str) -> set[str]:
        return set(self._automaton.find_matches_as_strings(text))

    def apply_rules(self, line: LineRecord) -> tuple[str, int]:
        hits = 0
        current_text = line.text
        matched_patterns = self.matched_patterns(current_text)

        for rule in self._rules:
            if rule.pattern not in matched_patterns:
                continue
            before = current_text
            updated_text = current_text.replace(rule.pattern, rule.replacement)
            if updated_text == before:
                continue
            current_text = updated_text
            if self.debug:
                before_snippet, after_snippet = _focus_diff(before, updated_text)
                logger.info(
                    'Applied rule {} to line {} | {} -> {}',
                    rule.name,
                    line.line_no,
                    before_snippet,
                    after_snippet,
                )

            hits += 1
            matched_patterns = self.matched_patterns(current_text)

        return current_text, hits


class RuleEngine:
    def __init__(self, rules_dir: Path, debug: bool = False):
        self.rules_dir = rules_dir
        self.debug = debug
        self.literal_rules, self.regex_rules, self.compiled_regex = self._load_rules()
        self.literal_matcher = LiteralPatternMatcher(self.literal_rules, debug=debug)

    def _load_rules(
        self,
    ) -> tuple[list[RuleDefinition], list[RuleDefinition], dict[int, CompiledRegex]]:
        literal_rules: list[RuleDefinition] = []
        regex_rules: list[RuleDefinition] = []
        compiled_regex: dict[int, CompiledRegex] = {}
        for rule_file in sorted(self.rules_dir.glob('*.json')):
            payload = json.loads(rule_file.read_text(encoding='utf-8'))
            for rule in RuleFile.model_validate(payload).enabled_rules():
                if not rule.regex:
                    literal_rules.append(rule)
                    continue

                try:
                    compiled_pattern = cast(CompiledRegex, regex.compile(rule.pattern))
                except regex.error as exc:
                    raise ValueError(f'Invalid regex rule "{rule.name}" in {rule_file.name}: {exc}') from exc
                regex_rules.append(rule)
                compiled_regex[id(rule)] = compiled_pattern

        return literal_rules, regex_rules, compiled_regex

    def apply_to_line(self, line: LineRecord) -> int:
        line.text, hits = self.literal_matcher.apply_rules(line)

        for rule in self.regex_rules:
            if self._apply_regex_rule(line, rule):
                hits += 1
        return hits

    def _apply_regex_rule(self, line: LineRecord, rule: RuleDefinition) -> bool:
        before = line.text
        compiled_pattern = self.compiled_regex.get(id(rule))
        if compiled_pattern is None:
            return False
        after = compiled_pattern.sub(rule.replacement, before)

        if after == before:
            return False
        if self.debug:
            before_snippet, after_snippet = _focus_diff(before, after)
            logger.info(
                'Applied rule {} to line {} | {} -> {}',
                rule.name,
                line.line_no,
                before_snippet,
                after_snippet,
            )
        line.text = after
        return True

    def apply(self, chapters: dict[int, ParsedChapter]) -> int:
        total_hits = 0
        for chapter in chapters.values():
            for line in chapter.body_lines:
                total_hits += self.apply_to_line(line)
        return total_hits


engine = RuleEngine(rules_dir=Path(__file__).parent / 'rules')
