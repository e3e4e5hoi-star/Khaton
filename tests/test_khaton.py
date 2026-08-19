from pathlib import Path
from khaton.bytecode import compile_source, run_bytecode
from khaton.lexer import COMMANDS, lex
from khaton.parser import parse
from khaton.runtime import KhatonRuntime
from khaton.stdlib import LIBRARIES, load_library

def test_command_and_library_contracts():
    assert len(COMMANDS) == 40
    assert len(LIBRARIES) == 17
    for name in LIBRARIES: assert load_library(name)

def test_interpreter_arithmetic_and_event():
    runtime = KhatonRuntime().run(parse('let x = 6\nlet y = 7\nmul answer x y\nadd answer answer 1\nassert answer\nprintty answer\nemit done answer'))
    assert runtime.output == ['43']
    assert runtime.events[0]['event'] == 'done'

def test_repeat_and_import():
    runtime = KhatonRuntime().run(parse('let n = 0\nrepeat 3\nadd n n 1\nend\nimport math'))
    assert runtime.env['n'] == 3 and 'sqrt' in runtime.env['math']

def test_const_and_if_else_regressions():
    runtime = KhatonRuntime().run(parse('const limit = 3\nif 0\nprintty bad\nelse\nprintty limit\nend'))
    assert runtime.output == ['3']
    try:
        KhatonRuntime().run(parse('const x = 1\nset x 2'))
        assert False
    except RuntimeError as exc:
        assert 'constant x cannot be reassigned' in str(exc)

def test_try_catch_finally():
    source = 'try begin\nassert 0\ntry catch as error\nprintty error\ntry finally\nprintty done\ntry end'
    runtime = KhatonRuntime().run(parse(source))
    assert runtime.output[0].startswith('line 2: assertion failed')
    assert runtime.output[1] == 'done'

def test_try_without_catch_propagates():
    try:
        KhatonRuntime().run(parse('try begin\nassert 0\ntry end'))
        assert False
    except RuntimeError as exc:
        assert 'assertion failed' in str(exc)

def test_bytecode_round_trip():
    program = compile_source('let x = 4\nadd y x 2\nprintty y')
    assert run_bytecode(program).output == ['6']

def test_parser_comments_and_quotes():
    assert lex('printty "hello world" # comment') == ['printty', 'hello world']
    assert parse('printty "hello"')[0].command == 'printty'


def test_legacy_print_is_rejected():
    try:
        parse('print "legacy"')
        assert False
    except SyntaxError as exc:
        assert 'unknown command print' in str(exc)


def test_repeat_zero_skips_body_and_nested_if_does_not_close_repeat():
    source = 'let n = 0\nrepeat 0\nadd n n 1\nend\nrepeat 2\nif 1\nadd n n 1\nend\nend'
    runtime = KhatonRuntime().run(parse(source))
    assert runtime.env['n'] == 2


def test_missing_arguments_report_runtime_error():
    for source in ('input', 'not', 'get', 'delete', 'new'):
        try:
            KhatonRuntime().run(parse(source))
            assert False
        except RuntimeError as exc:
            assert 'line 1:' in str(exc)


def test_bytecode_rejects_non_string_args_and_invalid_lines(tmp_path):
    from khaton.bytecode import load_bytecode
    malformed = tmp_path / 'bad.kbc'
    malformed.write_text('{"version": 1, "instructions": [{"op": "printty", "args": [3], "line": 0}]}', encoding='utf-8')
    try:
        load_bytecode(str(malformed))
        assert False
    except ValueError as exc:
        assert 'invalid Khaton instruction' in str(exc)


def test_cli_compile_closes_source_and_writes_bytecode(tmp_path):
    from khaton.cli import main
    source = tmp_path / 'sample.kh'
    output = tmp_path / 'sample.kbc'
    source.write_text('printty "ok"\n', encoding='utf-8')
    assert main(['compile', str(source), '-o', str(output)]) == 0
    assert output.exists()


def test_runtime_rejects_invalid_command_arguments():
    for source, message in (
        ('set', 'set requires'),
        ('assert', 'assert requires'),
        ('emit', 'emit requires'),
        ('sleep -1', 'sleep duration cannot be negative'),
    ):
        try:
            KhatonRuntime().run(parse(source))
            assert False
        except RuntimeError as exc:
            assert message in str(exc)


def test_deli_branching_and_legacy_elif_rejection():
    source = 'let score = 2\nif 0\nprintty wrong\nDeli score\nprintty middle\nelse\nprintty fallback\nend'
    runtime = KhatonRuntime().run(parse(source))
    assert runtime.output == ['middle']
    try:
        parse('elif 1')
        assert False
    except SyntaxError as exc:
        assert 'unknown command elif' in str(exc)
