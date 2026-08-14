from __future__ import annotations
import json, math, os, random, statistics, time, hashlib, re, pathlib, datetime, uuid

LIBRARIES = ('math','stats','strings','collections','json','os','path','time','random','crypto','regex','datetime','uuid','io','net','data','system')
def load_library(name: str):
    libs = {
        'math': {'pi': math.pi, 'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos},
        'stats': {'mean': statistics.mean, 'median': statistics.median},
        'strings': {'upper': str.upper, 'lower': str.lower, 'strip': str.strip},
        'collections': {'list': list, 'tuple': tuple},
        'json': {'encode': json.dumps, 'decode': json.loads},
        'os': {'cwd': os.getcwd, 'env': dict(os.environ)},
        'path': {'join': os.path.join, 'exists': os.path.exists},
        'time': {'now': time.time, 'sleep': time.sleep},
        'random': {'random': random.random, 'choice': random.choice},
        'crypto': {'sha256': lambda x: hashlib.sha256(str(x).encode()).hexdigest()},
        'regex': {'match': re.match, 'search': re.search},
        'datetime': {'now': datetime.datetime.now},
        'uuid': {'new': uuid.uuid4},
        'io': {'read': lambda p: pathlib.Path(p).read_text()},
        'net': {'url_scheme': lambda u: u.split(':',1)[0]},
        'data': {'min': min, 'max': max, 'sum': sum},
        'system': {'platform': os.name, 'version': os.sys.version},
    }
    if name not in libs: raise ImportError(f'unknown standard library: {name}')
    return libs[name]
