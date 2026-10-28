# Old vaults under a new build.  Step "make" runs under the OLD sgit-ai (any version), "open" under the build under test.
#   python -I legacy_vault.py make W [packs]     old build: init, 6 commits (add, edit, rename, delete, nested folders), push; saves the host
#   python -I legacy_vault.py open W             new build: (1) opens the OLD working copy (status, fsck, commit, push),
#                                                (2) clones the vault from the host (fsck, log, verify), (3) old tree == new clone tree
#   python -I legacy_vault.py reopen W           old build again: pulls what the new build pushed and fsck
import os, sys, pickle, json, traceback, shutil
step, W = sys.argv[1], sys.argv[2]
import sgit_ai
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup(); state = os.path.join(W, 'host.pickle')
if os.path.exists(state): api._store, api._tombstones = pickle.load(open(state, 'rb'))
s = Vault__Sync(crypto=Vault__Crypto(), api=api); a = os.path.join(W, 'a'); c = os.path.join(W, 'c')
VER = open(os.path.join(os.path.dirname(sgit_ai.__file__), 'version')).read().strip(); out = {'step': step, 'sgit': VER}
def put(r, t):
    p = os.path.join(a, r); os.makedirs(os.path.dirname(p) or a, exist_ok=True); open(p, 'w').write(t)
def tree(b):
    o = {}
    for r, ds, fs in os.walk(b):
        ds[:] = [x for x in ds if x != '.sg_vault']
        for f in fs: o[os.path.relpath(os.path.join(r, f), b)] = open(os.path.join(r, f)).read()
    return o
def attempt(k, fn):
    try: out[k] = fn()
    except Exception as e: out[k] = f'ERROR {type(e).__name__}: {str(e)[:160]}'
fs = lambda d: {k: (len(v) if isinstance(v, list) else v) for k, v in s.fsck(d).items() if k in ('ok', 'missing', 'corrupt', 'errors')}
if step == 'make':
    os.makedirs(W, exist_ok=True); kw = dict(packs=True) if len(sys.argv) > 3 else {}
    key = s.init(a, **kw)['vault_key']; open(os.path.join(W, 'key.txt'), 'w').write(key)
    put('README.md', 'hello\nworld\n'); put('docs/guide.md', ''.join(f'guide line {i}\n' for i in range(30))); put('src/app.py', 'def f():\n    return 1\n')
    s.commit(a, message='first'); s.push(a)
    put('src/app.py', 'def f():\n    return 2  # needle\n'); s.commit(a, message='edit')
    os.rename(os.path.join(a, 'docs/guide.md'), os.path.join(a, 'docs/manual.md')); s.commit(a, message='rename guide')
    put('deep/er/est/x.txt', 'deep\n'); s.commit(a, message='nested')
    os.remove(os.path.join(a, 'README.md')); s.commit(a, message='delete readme'); s.push(a)
    out['made'] = 'ok'
elif step == 'open':
    attempt('old-copy status', lambda: str(s.status(a))[:0] or 'ok'); attempt('old-copy fsck', lambda: fs(a))
    put('new.txt', 'from the new build\n')
    attempt('old-copy commit+push', lambda: (s.commit(a, message='new build'), s.push(a), 'ok')[2])
    key = open(os.path.join(W, 'key.txt')).read().strip()
    attempt('fresh clone', lambda: (s.clone(key, c), 'ok')[1]); attempt('clone fsck', lambda: fs(c))
    attempt('verify', lambda: (lambda r: r['counts'])(s.verify_signatures(c)))
    attempt('trees equal', lambda: tree(a) == tree(c))
elif step == 'reopen':
    attempt('pull', lambda: (s.pull(a), 'ok')[1]); out['new.txt'] = os.path.exists(os.path.join(a, 'new.txt')); attempt('fsck', lambda: fs(a))
pickle.dump((api._store, api._tombstones), open(state, 'wb')); print(json.dumps(out))
