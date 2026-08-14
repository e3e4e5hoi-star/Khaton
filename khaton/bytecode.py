from __future__ import annotations
import json
from .parser import parse

def compile_source(source: str) -> dict:
    statements = parse(source)
    return {'version': 1, 'instructions': [{'op': s.command, 'args': list(s.args), 'line': s.line} for s in statements]}

def save_bytecode(program: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f: json.dump(program, f, indent=2)

def load_bytecode(path: str) -> dict:
    with open(path, encoding='utf-8') as f: program = json.load(f)
    if program.get('version') != 1 or not isinstance(program.get('instructions'), list): raise ValueError('invalid Khaton bytecode')
    for instruction in program['instructions']:
        if not isinstance(instruction, dict) or instruction.get('op') not in __import__('khaton.lexer', fromlist=['COMMANDS']).COMMANDS or not isinstance(instruction.get('args'), list) or not isinstance(instruction.get('line'), int):
            raise ValueError('invalid Khaton instruction')
    return program

def run_bytecode(program: dict):
    from .runtime import KhatonRuntime
    from .parser import Statement
    statements = [Statement(x['op'], tuple(x['args']), int(x['line'])) for x in program['instructions']]
    return KhatonRuntime().run(statements)
