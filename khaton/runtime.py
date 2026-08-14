from __future__ import annotations
import ast, time
from .parser import Statement
from .stdlib import load_library

class KhatonRuntime:
    def __init__(self): self.env = {}; self.output = []; self.events = []
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
                    self.env[a[0]] = self.value(' '.join(a[2:]))
                elif c == 'print': self.output.append(' '.join(str(self.value(x)) for x in a))
                elif c == 'input': self.env[a[0]] = input(' '.join(a[1:]))
                elif c in {'add','sub','mul','div','mod','eq','lt','gt','and','or'}:
                    if len(a) != 3: raise ValueError(f'{c} requires target left right')
                    x, y = self.value(a[1]), self.value(a[2]); ops={'add':lambda:x+y,'sub':lambda:x-y,'mul':lambda:x*y,'div':lambda:x/y,'mod':lambda:x%y,'eq':lambda:x==y,'lt':lambda:x<y,'gt':lambda:x>y,'and':lambda:bool(x) and bool(y),'or':lambda:bool(x) or bool(y)}; self.env[a[0]]=ops[c]()
                elif c == 'not': self.env[a[0]] = not bool(self.value(a[1]))
                elif c == 'set': self.env[a[0]] = self.value(' '.join(a[2:])) if len(a)>2 and a[1]=='=' else self.value(a[1])
                elif c == 'get': self.output.append(str(self.env.get(a[0], None)))
                elif c == 'assert':
                    if not bool(self.value(a[0])): raise AssertionError('assertion failed')
                elif c == 'emit': self.events.append({'event': a[0], 'payload': [self.value(x) for x in a[1:]]})
                elif c == 'sleep': time.sleep(float(self.value(a[0])))
                elif c == 'import': self.env[a[0]] = load_library(a[0])
                elif c == 'repeat': repeat_stack.append((pc, int(self.value(a[0]))))
                elif c == 'end' and repeat_stack:
                    start, remaining = repeat_stack[-1]
                    if remaining > 1: repeat_stack[-1] = (start, remaining-1); pc = start
                    else: repeat_stack.pop()
                elif c in {'if','while','fn','return','call','export','match','case','break','continue','type','struct','enum','new','delete','else'}:
                    if c == 'return': self.env['_return'] = self.value(a[0]) if a else None
                    elif c == 'break': break
                    elif c == 'delete': self.env.pop(a[0], None)
                    elif c == 'new': self.env[a[0]] = {}
                else: raise ValueError(f'unsupported command {c}')
            except Exception as exc: raise RuntimeError(f'line {s.line}: {exc}') from exc
            pc += 1
        return self
