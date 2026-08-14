from pathlib import Path
from khaton.bytecode import compile_source, run_bytecode
from khaton.lexer import COMMANDS, lex
from khaton.parser import parse
from khaton.runtime import KhatonRuntime
from khaton.stdlib import LIBRARIES, load_library

def test_command_and_library_contracts():
    assert len(COMMANDS) == 38
    assert len(LIBRARIES) == 17
    for name in LIBRARIES: assert load_library(name)

def test_interpreter_arithmetic_and_event():
    runtime = KhatonRuntime().run(parse('let x = 6\nlet y = 7\nmul answer x y\nadd answer answer 1\nassert answer\nprint answer\nemit done answer'))
    assert runtime.output == ['43']
    assert runtime.events[0]['event'] == 'done'

def test_repeat_and_import():
    runtime = KhatonRuntime().run(parse('let n = 0\nrepeat 3\nadd n n 1\nend\nimport math'))
    assert runtime.env['n'] == 3 and 'sqrt' in runtime.env['math']

def test_const_and_if_else_regressions():
    runtime = KhatonRuntime().run(parse('const limit = 3\nif 0\nprint bad\nelse\nprint limit\nend'))
    assert runtime.output == ['3']
    try:
        KhatonRuntime().run(parse('const x = 1\nset x 2'))
        assert False
    except RuntimeError as exc:
        assert 'constant x cannot be reassigned' in str(exc)

def test_bytecode_round_trip():
    program = compile_source('let x = 4\nadd y x 2\nprint y')
    assert run_bytecode(program).output == ['6']

def test_parser_comments_and_quotes():
    assert lex('print "hello world" # comment') == ['print', 'hello world']
    assert parse('print "hello"')[0].command == 'print'
