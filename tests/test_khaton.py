from pathlib import Path
from khaton.bytecode import compile_source, run_bytecode
from khaton.lexer import COMMANDS, lex
from khaton.parser import parse
from khaton.runtime import KhatonRuntime
from khaton.stdlib import LIBRARIES, load_library

def test_command_and_library_contracts():
    assert len(COMMANDS) == 39
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
