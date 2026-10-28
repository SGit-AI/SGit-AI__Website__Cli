# BR-1 repair: STEP make (run with 0.26.8 or older: one push of N commits leaves a gap), STEP repair (0.26.9+: check upload-history).
#   python -I gap_repair.py make W N [packs]     |     python -I gap_repair.py repair W
import os, sys, pickle, json
step, W = sys.argv[1], sys.argv[2]
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup(); state = os.path.join(W, 'host.pickle')
if os.path.exists(state): api._store, api._tombstones = pickle.load(open(state, 'rb'))
s = Vault__Sync(crypto=Vault__Crypto(), api=api); a, c = os.path.join(W, 'a'), os.path.join(W, 'c')
def put(r, t): open(os.path.join(a, r), 'w').write(t)
fs = lambda d: {k: (len(v) if isinstance(v, list) else v) for k, v in s.fsck(d).items() if k in ('ok', 'missing', 'corrupt', 'errors')}
out = {}
if step == 'make':
    os.makedirs(W, exist_ok=True); n = int(sys.argv[3])
    key = s.init(a, packs=True)['vault_key'] if len(sys.argv) > 4 else s.init(a)['vault_key']; open(os.path.join(W, 'key.txt'), 'w').write(key)
    put('x.txt', '0\n'); s.commit(a, message='first'); s.push(a)
    for i in range(n): put('x.txt', f'{i+1}\n'); s.commit(a, message=f'c{i}')
    s.push(a); put('x.txt', 'later\n'); s.commit(a, message='later'); s.push(a)
    s.clone(key, c); out['before repair: fresh clone fsck'] = fs(c)
else:
    key = open(os.path.join(W, 'key.txt')).read().strip()
    out['dry-run'] = {k: v for k, v in s.upload_history(a, dry_run=True).items() if not isinstance(v, (list, dict))}
    out['repair']  = {k: v for k, v in s.upload_history(a).items() if not isinstance(v, (list, dict))}
    import shutil; shutil.rmtree(c, ignore_errors=True); s.clone(key, c); out['after repair: fresh clone fsck'] = fs(c)
    n = 0; cid = s.resolve_revision(c, 'HEAD')
    out['log'] = len([e for e in s.log(c)]) if hasattr(s, 'log') else 'n/a'
pickle.dump((api._store, api._tombstones), open(state, 'wb')); print(json.dumps(out))
