from __future__ import annotations
import ast, time
from .parser import Statement
from .stdlib import load_library

class KhatonRuntime:
    def __init__(self): self.env = {}; self.constants = set(); self.output = []; self.events = []
    def _run_try(self, statements, start: int):
        catch_at = finally_at = end_at = None
        depth = 0
        for index in range(start + 1, len(statements)):
            args = statements[index].args
            if statements[index].command == 'try':
                mode = args[0] if args else ''
                if mode == 'begin': depth += 1
                elif mode == 'end':
                    if depth: depth -= 1
                    else: end_at = index; break
                elif depth == 0 and mode == 'catch': catch_at = index
                elif depth == 0 and mode == 'finally': finally_at = index
        if end_at is None: raise SyntaxError('try block requires try end')
        if catch_at is not None and finally_at is not None and catch_at > finally_at: raise SyntaxError('try catch must precede try finally')
        body_end = min(x for x in (catch_at, finally_at, end_at) if x is not None)
        caught = None
        try: self.run(statements[start + 1:body_end])
        except RuntimeError as exc:
            caught = exc
            if catch_at is not None:
                catch_end = finally_at if finally_at is not None else end_at
                catch_args = statements[catch_at].args
                if len(catch_args) >= 3 and catch_args[1] == 'as': self.env[catch_args[2]] = str(exc)
                elif len(catch_args) >= 2: self.env[catch_args[1]] = str(exc)
                self.run(statements[catch_at + 1:catch_end])
            else: raise
        finally:
            if finally_at is not None: self.run(statements[finally_at + 1:end_at])
        return end_at

    @staticmethod
    def _block_end(statements, start: int):
        depth = 0
        for index in range(start + 1, len(statements)):
            command = statements[index].command
            if command in {'if', 'while', 'repeat', 'fn'}: depth += 1
            elif command == 'end':
                if depth == 0: return index
                depth -= 1
        raise SyntaxError(f"line {statements[start].line}: block requires end")
    @staticmethod
    def _jump_to(statements, pc, targets):
        depth = 0
        for index in range(pc + 1, len(statements)):
            command = statements[index].command
            if command in {'if', 'while', 'repeat', 'fn'}: depth += 1
            elif command == 'end':
                if depth == 0: return index
                depth -= 1
            elif command == 'else' and depth == 0 and targets == {'else'}: return index
        return len(statements)
    def value(self, text: str):
        if text in self.env: return self.env[text]
        try: return ast.literal_eval(text)
        except (ValueError, SyntaxError): return text
    def run(self, statements: list[Statement]):
        pc = 0; repeat_stack = []
        while pc < len(statements):
            s = statements[pc]; c, a = s.command, s.args
            try:
                if c in {'let','const'}:
                    if len(a) < 3 or a[1] != '=': raise ValueError('syntax: let name = value')
                    if a[0] in self.constants: raise ValueError(f'constant {a[0]} cannot be reassigned')
                    self.env[a[0]] = self.value(' '.join(a[2:]))
                    if c == 'const': self.constants.add(a[0])
                elif c == 'printty': self.output.append(' '.join(str(self.value(x)) for x in a))
                elif c == 'input':
                    if not a: raise ValueError('input requires a target variable')
                    self.env[a[0]] = input(' '.join(a[1:]))
                elif c in {'add','sub','mul','div','mod','eq','lt','gt','and','or'}:
                    if len(a) != 3: raise ValueError(f'{c} requires target left right')
                    x, y = self.value(a[1]), self.value(a[2]); ops={'add':lambda:x+y,'sub':lambda:x-y,'mul':lambda:x*y,'div':lambda:x/y,'mod':lambda:x%y,'eq':lambda:x==y,'lt':lambda:x<y,'gt':lambda:x>y,'and':lambda:bool(x) and bool(y),'or':lambda:bool(x) or bool(y)}; self.env[a[0]]=ops[c]()
                elif c == 'not':
                    if len(a) != 2: raise ValueError('not requires target and value')
                    self.env[a[0]] = not bool(self.value(a[1]))
                elif c == 'set':
                    if len(a) < 2: raise ValueError('set requires a variable and value')
                    if a[0] in self.constants: raise ValueError(f'constant {a[0]} cannot be reassigned')
                    self.env[a[0]] = self.value(' '.join(a[2:])) if len(a)>2 and a[1]=='=' else self.value(a[1])
                elif c == 'get':
                    if len(a) != 1: raise ValueError('get requires a variable')
                    self.output.append(str(self.env.get(a[0], None)))
                elif c == 'assert':
                    if len(a) != 1: raise ValueError('assert requires one condition')
                    if not bool(self.value(a[0])): raise AssertionError('assertion failed')
                elif c == 'emit':
                    if not a: raise ValueError('emit requires an event name')
                    self.events.append({'event': a[0], 'payload': [self.value(x) for x in a[1:]]})
                elif c == 'sleep':
                    if len(a) != 1: raise ValueError('sleep requires one duration')
                    duration = float(self.value(a[0]))
                    if duration < 0: raise ValueError('sleep duration cannot be negative')
                    time.sleep(duration)
                elif c == 'try':
                    if not a or a[0] != 'begin': raise ValueError('use try begin, try catch [as name], try finally, try end')
                    pc = self._run_try(statements, pc)
                elif c == 'import': self.env[a[0]] = load_library(a[0])
                elif c == 'if':
                    if not a: raise ValueError('if requires a condition')
                    if not bool(self.value(a[0])): pc = self._jump_to(statements, pc, {'else'})
                elif c == 'else': pc = self._jump_to(statements, pc, set())
                elif c == 'repeat':
                    if len(a) != 1: raise ValueError('repeat requires one non-negative count')
                    count = int(self.value(a[0]))
                    if count < 0: raise ValueError('repeat requires a non-negative count')
                    end_at = self._block_end(statements, pc)
                    if count == 0:
                        pc = end_at
                    else:
                        repeat_stack.append((pc, count, end_at))
                elif c == 'end' and repeat_stack and pc == repeat_stack[-1][2]:
                    start, remaining, end_at = repeat_stack[-1]
                    if remaining > 1: repeat_stack[-1] = (start, remaining - 1, end_at); pc = start
                    else: repeat_stack.pop()
                elif c == 'end':
                    pass
                elif c in {'while','fn','return','call','match','case','break','continue','type','struct','enum','new','delete'}:
                    if c == 'return': self.env['_return'] = self.value(a[0]) if a else None
                    elif c == 'break': break
                    elif c == 'delete':
                        if len(a) != 1: raise ValueError('delete requires a variable')
                        self.env.pop(a[0], None)
                    elif c == 'new':
                        if len(a) != 1: raise ValueError('new requires a variable')
                        self.env[a[0]] = {}
                else: raise ValueError(f'unsupported command {c}')
            except Exception as exc: raise RuntimeError(f'line {s.line}: {exc}') from exc
            pc += 1
        return self
