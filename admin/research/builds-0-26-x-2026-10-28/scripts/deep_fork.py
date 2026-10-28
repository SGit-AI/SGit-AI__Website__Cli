# A fork N commits deep on each side, disjoint files: does `pull` merge cleanly?
#   [BATCH=50] python -I deep_fork.py N [N ...]
import os, sys, tempfile, time
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
def put(b, r, t):
    p = os.path.join(b, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)
BATCH = int(os.environ.get('BATCH', '0'))         # push every BATCH commits (0: one push), to keep the push gap out
for N in map(int, sys.argv[1:]):
    api = Vault__API__In_Memory().setup(); s = Vault__Sync(crypto=Vault__Crypto(), api=api); W = tempfile.mkdtemp()
    a, b = os.path.join(W, 'a'), os.path.join(W, 'b')
    key = s.init(a)['vault_key']
    put(a, 'a/x.txt', '0\n'); put(a, 'b/y.txt', '0\n'); s.commit(a, message='first'); s.push(a); s.clone(key, b)
    for i in range(N):
        put(a, 'a/x.txt', f'{i+1}\n'); s.commit(a, message=f'a{i}')
        put(b, 'b/y.txt', f'{i+1}\n'); s.commit(b, message=f'b{i}')
        if BATCH and i % BATCH == BATCH - 1: s.push(a)
    s.push(a)
    try: r = s.pull(b); err = ''
    except Exception as e: r = {}; err = f'{type(e).__name__}: {str(e)[:100]}'
    conf = sorted(os.path.relpath(os.path.join(x, f), b) for x, _, fs in os.walk(b) for f in fs if f.endswith('.conflict'))
    x, y = open(os.path.join(b, 'a/x.txt')).read().strip(), open(os.path.join(b, 'b/y.txt')).read().strip()
    ok = not conf and not err and x == str(N) and y == str(N)
    print(f'  {"✓" if ok else "✗"} N={N:<4} a/x.txt={x:<4} b/y.txt={y:<4} conflicts={conf} {err}')
