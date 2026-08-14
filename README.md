# Khaton — خاتون

Khaton is a compact experimental programming language inspired by the explicit, performance-oriented spirit of C++ and the expressive functional style of F#. It currently provides a safe line-oriented syntax, a deterministic interpreter, a JSON bytecode format and 17 standard libraries.

> Khaton is an educational language implementation. It is not a drop-in replacement for C++ or F#, and it does not claim native-machine performance yet.

## 39 commands

`let`, `const`, `print`, `input`, `if`, `else`, `end`, `repeat`, `while`, `fn`, `return`, `call`, `import`, `match`, `case`, `break`, `continue`, `assert`, `type`, `struct`, `enum`, `new`, `delete`, `set`, `get`, `add`, `sub`, `mul`, `div`, `mod`, `eq`, `lt`, `gt`, `and`, `or`, `not`, `emit`, `sleep`, and `try`.

The core executable semantics cover immutable constants, variable binding, output, input, arithmetic and boolean operations, assertions, imports, if/else blocks, bounded repeat loops, event emission, sleep, basic object storage, bytecode compilation, and structured exception handling. The remaining reserved commands are part of the forward-compatible grammar and produce explicit behavior or safe no-op semantics while the language grows.

## 17 standard libraries

`math`, `stats`, `strings`, `collections`, `json`, `os`, `path`, `time`, `random`, `crypto`, `regex`, `datetime`, `uuid`, `io`, `net`, `data`, and `system`.

## Two ways to run Khaton

### 1. Direct interpreter

```bash
python -m khaton run examples/hello.kh
```

### 2. Compile to JSON bytecode and execute it

```bash
python -m khaton compile examples/hello.kh -o hello.kbc
python -m khaton exec hello.kbc
```

The bytecode format is versioned JSON for transparency and debugging. It is not intended to be treated as a security boundary for untrusted files.

## Example

```khaton
import math
let x = 6
let y = 7
mul product x y
print product
add answer product 1
assert answer
emit calculation answer
```

## Khaton Studio desktop app

Khaton Studio is a lightweight Tkinter desktop editor included in `studio/`. It provides line numbers, colored Khaton commands, colored numbers and strings, the submitted camel logo, file open/save, direct Run, bytecode Compile, and an output/diagnostics panel.

Run it from the source tree on Windows, Linux or macOS:

```bash
python studio/khaton_studio.py
```

On Windows, the standalone `KhatonStudio.exe` is built by the GitHub Actions workflow `.github/workflows/build-studio-windows.yml`. Open the repository's **Actions** tab, run **Build Khaton Studio for Windows**, then download the `KhatonStudio-Windows` artifact. To build from a tag, push a tag such as `studio-v0.2.0`; the workflow will create the same Windows artifact.

## Installation and tests

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
```

The regression suite covers constants, conditional blocks, bytecode validation, parser comments, exception handling and both execution paths.

## Exception handling

Khaton uses one command family, `try`, with explicit modes. The `try begin` block is executed normally; `try catch as name` receives a caught runtime error; `try finally` always executes; and `try end` closes the construct.

```khaton
try begin
  assert 0
try catch as error
  print error
try finally
  print cleanup
try end
```

Exceptions that are not caught are re-raised with the source line number. The construct is also supported by the bytecode path because bytecode stores the same statements.

The implementation is intentionally small and testable. Future work includes a typed AST, real pattern matching, closures, a register-based VM, native extensions, package resolution and static analysis.

## License

MIT License. See [LICENSE](LICENSE).
