from pathlib import Path
from khaton.bytecode import compile_source, run_bytecode
from khaton.lexer import COMMANDS, lex
from khaton.parser import parse
from khaton.runtime import KhatonRuntime
from khaton.stdlib import LIBRARIES, load_library

def test_command_and_library_contracts():
    assert len(COMMANDS) == 41
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


def test_large_repeat_has_reasonable_runtime():
    from time import perf_counter
    source = 'let n = 0\nrepeat 5000\nif 1\nadd n n 1\nend\nend\nprintty n'
    started = perf_counter()
    runtime = KhatonRuntime().run(parse(source))
    elapsed = perf_counter() - started
    assert runtime.output == ['5000']
    assert elapsed < 2.0


def test_repeat_requires_an_integer_not_a_truncated_float_or_bool():
    for value in ('2.5', 'True'):
        try:
            KhatonRuntime().run(parse(f'repeat {value}\nprintty bad\nend'))
            assert False
        except RuntimeError as exc:
            assert 'repeat requires an integer count' in str(exc)


def test_import_requires_exactly_one_library_name():
    try:
        KhatonRuntime().run(parse('import math extra'))
        assert False
    except RuntimeError as exc:
        assert 'import requires one library name' in str(exc)


def test_declared_but_unimplemented_commands_fail_loudly():
    for command in ('while', 'fn', 'call', 'match', 'case'):
        try:
            KhatonRuntime().run(parse(command))
            assert False
        except RuntimeError as exc:
            assert f'{command} is not implemented yet' in str(exc)


def test_studio_source_launcher_uses_repository_root_and_real_newlines():
    studio_source = Path('studio/khaton_studio.py').read_text(encoding='utf-8')
    assert "Path(__file__).resolve().parent.parent" in studio_source
    assert 'self._write_output("\\n".join(result.output)' in studio_source
    assert 'self._write_output("\\\\n".join(result.output)' not in studio_source


def test_args_command_receives_cli_values_and_does_not_alias_input():
    runtime = KhatonRuntime().run(parse('args received\nprintty received'), argv=['alpha', 'beta'])
    assert runtime.env['received'] == ['alpha', 'beta']
    assert runtime.output == ["['alpha', 'beta']"]


def test_args_command_requires_one_target():
    try:
        KhatonRuntime().run(parse('args'))
        assert False
    except RuntimeError as exc:
        assert 'args requires one target variable' in str(exc)


def test_bytecode_and_cli_forward_program_args(tmp_path, capsys):
    from khaton.cli import main
    source = tmp_path / 'args.kh'
    bytecode = tmp_path / 'args.kbc'
    source.write_text('args received\nprintty received\n', encoding='utf-8')
    assert main(['compile', str(source), '-o', str(bytecode)]) == 0
    capsys.readouterr()
    assert main(['exec', str(bytecode), 'one', 'two']) == 0
    assert capsys.readouterr().out.strip() == "['one', 'two']"


def test_runtime_does_not_leak_cli_args_between_top_level_runs():
    runtime = KhatonRuntime()
    runtime.run(parse('args received'), argv=['old'])
    runtime.run(parse('args received'))
    assert runtime.env['received'] == []


def test_args_are_preserved_inside_try_and_reserved_target_is_rejected():
    runtime = KhatonRuntime().run(parse('try begin\nargs received\ntry end\nprintty received'), argv=['kept'])
    assert runtime.output == ["['kept']"]
    try:
        KhatonRuntime().run(parse('args _argv'), argv=['x'])
        assert False
    except RuntimeError as exc:
        assert 'args target cannot be _argv' in str(exc)
