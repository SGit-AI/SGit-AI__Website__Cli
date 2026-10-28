# One step of the cross-version check: load the in-memory host from W/host.pickle, act as this Python's sgit,
# save it back. Steps: new-create, old-follow, new-follow, new-long, old-after-long.
import os, sys, pickle, json
STEP, W = sys.argv[1], sys.argv[2]
import sgit_ai
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup(); state = os.path.join(W, 'host.pickle')
if os.path.exists(state): api._store, api._tombstones = pickle.load(open(state, 'rb'))
s = Vault__Sync(crypto=Vault__Crypto(), api=api); d = lambda n: os.path.join(W, n)
VER = open(os.path.join(os.path.dirname(sgit_ai.__file__), 'version')).read().strip()
def put(b, r, t):
    p = os.path.join(b, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)
def tree(b):
    out = {}
    for r, ds, fs in os.walk(b):
        ds[:] = [x for x in ds if x != '.sg_vault']
        for f in fs: out[os.path.relpath(os.path.join(r, f), b)] = open(os.path.join(r, f)).read()
    return out
out = {'step': STEP, 'sgit': VER}
try:
    if STEP == 'new-create':
        key = s.init(d('n'))['vault_key']; open(d('key.txt'), 'w').write(key)
        put(d('n'), 'notes.md', ''.join(f'line {i}\n' for i in range(20))); put(d('n'), 'a.txt', 'a\n'); put(d('n'), 'b.txt', 'b\n')
        s.commit(d('n'), message='first'); s.push(d('n'))
        put(d('n'), 'a.txt', 'a2\n'); put(d('n'), 'b.txt', 'b2 (left uncommitted)\n')
        s.commit(d('n'), message='paths', paths=['a.txt'])
        put(d('n'), 'notes.md', ''.join(f'line {i}{" edited" if i in (2, 15) else ""}\n' for i in range(20)))
        h = s.list_hunks(d('n'), paths=['notes.md']).files[0].hunks
        s.commit(d('n'), message='one hunk', hunks=[str(h[0].hunk_id)]); s.push(d('n'))
        out['hunks'] = len(h)
    elif STEP == 'old-follow':
        key = open(d('key.txt')).read().strip(); s.clone(key, d('o')); t = tree(d('o'))
        out['a.txt'] = t['a.txt']; out['b.txt'] = t['b.txt']; out['line 2 / 15'] = [l for l in t['notes.md'].splitlines() if l.startswith(('line 2', 'line 15'))]
        put(d('o'), 'c.txt', 'from the old client\n'); s.commit(d('o'), message='old'); s.push(d('o'))
    elif STEP == 'new-follow':
        s.pull(d('n')); t = tree(d('n')); out['c.txt'] = t.get('c.txt'); out['b.txt kept'] = t['b.txt']
    elif STEP == 'new-long':
        s.set_format(d('n'), add_features=['long-messages'])
        put(d('n'), 'a.txt', 'a3\n'); s.commit(d('n'), message='L' * 10000, paths=['a.txt']); s.push(d('n'))
        out['pushed'] = '10,000-byte message'
    elif STEP == 'old-after-long':
        try: s.pull(d('o')); out['pull'] = 'went through'
        except Exception as e: out['pull'] = f'refused: {type(e).__name__}: {str(e)[:150]}'
except Exception as e:
    out['error'] = f'{type(e).__name__}: {str(e)[:200]}'
pickle.dump((api._store, api._tombstones), open(state, 'wb'))
print(json.dumps(out))
