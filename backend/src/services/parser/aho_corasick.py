"""Minimal Aho–Corasick multi-pattern literal search (pure Python)."""

from __future__ import annotations

from collections import deque
from typing import Sequence


class _TrieNode:
    __slots__ = ('children', 'fail', 'output')

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.fail: _TrieNode | None = None
        self.output: list[str] = []


class AhoCorasick:
    """Find which literal patterns from a fixed set occur in a string (each pattern at most once in the result set per scan)."""

    def __init__(self, patterns: Sequence[str]) -> None:
        self._root = _TrieNode()
        for p in dict.fromkeys(patterns):
            if not p:
                continue
            node = self._root
            for ch in p:
                node = node.children.setdefault(ch, _TrieNode())
            node.output.append(p)
        self._build_failure_links()

    def _build_failure_links(self) -> None:
        root = self._root
        queue: deque[_TrieNode] = deque()
        for child in root.children.values():
            child.fail = root
            queue.append(child)
        while queue:
            state = queue.popleft()
            for ch, child in state.children.items():
                queue.append(child)
                f = state.fail
                while f is not None and ch not in f.children:
                    f = f.fail
                child.fail = f.children[ch] if f is not None and ch in f.children else root
                child.output.extend(child.fail.output)

    def find_matches_as_strings(self, text: str) -> set[str]:
        found: set[str] = set()
        node = self._root
        for ch in text:
            while node is not self._root and ch not in node.children:
                fail = node.fail
                assert fail is not None
                node = fail
            if ch in node.children:
                node = node.children[ch]
            found.update(node.output)
        return found
