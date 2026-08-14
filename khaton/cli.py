from __future__ import annotations
import argparse
from .bytecode import compile_source, load_bytecode, run_bytecode, save_bytecode
from .parser import parse
from .runtime import KhatonRuntime

def main(argv=None):
    p = argparse.ArgumentParser(prog='khaton'); sub = p.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run'); run.add_argument('file')
    comp = sub.add_parser('compile'); comp.add_argument('file'); comp.add_argument('-o', '--output', required=True)
    exe = sub.add_parser('exec'); exe.add_argument('file')
    args = p.parse_args(argv)
    if args.action == 'run': result = KhatonRuntime().run(parse(open(args.file, encoding='utf-8').read()))
    elif args.action == 'compile': save_bytecode(compile_source(open(args.file, encoding='utf-8').read()), args.output); print(f'compiled {args.file} -> {args.output}'); return 0
    else: result = run_bytecode(load_bytecode(args.file))
    print('\n'.join(result.output)); return 0
