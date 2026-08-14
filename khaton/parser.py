from __future__ import annotations
from dataclasses import dataclass
from .lexer import COMMANDS, lex

@dataclass(frozen=True)
class Statement:
    command: str
    args: tuple[str, ...]
    line: int

def parse(source: str) -> list[Statement]:
    result = []
    for number, raw in enumerate(source.splitlines(), 1):
        words = lex(raw.strip())
        if not words: continue
        if words[0] not in COMMANDS: raise SyntaxError(f"line {number}: unknown command {words[0]}")
        result.append(Statement(words[0], tuple(words[1:]), number))
    return result
