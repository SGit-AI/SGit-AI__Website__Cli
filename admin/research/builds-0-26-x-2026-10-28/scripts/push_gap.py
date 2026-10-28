# One push of N commits, then one more push: does the host hold every commit? A fresh clone walks the history
# (init's commit + 'first' + N + 1) and runs fsck.
#   python -I push_gap.py N [N ...]
import os, sys, tempfile
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.crypto.PKI__Crypto import PKI__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.storage.Vault__Commit import Vault__Commit
from sgit_ai.storage.Vault__Ref_Manager import Vault__Ref_Manager
def put(b, r, t):
    p = os.path.join(b, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)
for N in map(int, sys.argv[1:]):
    api = Vault__API__In_Memory().setup(); s = Vault__Sync(crypto=Vault__Crypto(), api=api); W = tempfile.mkdtemp()
    a, c = os.path.join(W, 'a'), os.path.join(W, 'c')
    key = s.init(a, packs=True)['vault_key'] if os.environ.get('PACKS') else s.init(a)['vault_key']; put(a, 'x.txt', '0\n'); s.commit(a, message='first'); s.push(a)
    for i in range(N):
        put(a, 'x.txt', f'{i+1}\n'); s.commit(a, message=f'c{i}')
    s.push(a)                                                   # one push of N commits
    put(a, 'x.txt', 'later\n'); s.commit(a, message='a later commit'); s.push(a)   # does a later push fill the gap?
    s.clone(key, c)
    N += 1
    comp = s._init_components(c)
    vc = Vault__Commit(crypto=s.crypto, pki=PKI__Crypto(), object_store=comp.obj_store, ref_manager=Vault__Ref_Manager())
    cid, walked, missing = s.resolve_revision(c, 'HEAD'), 0, None
    from sgit_ai.core.actions.fetch.Vault__Fetch import Vault__Fetch
    while cid:
        try:
            if not comp.obj_store.exists(cid):
                data = api.read(comp.vault_id if hasattr(comp, 'vault_id') else None, f'bare/data/{cid}')
            commit = vc.load_commit(cid, comp.read_key)
        except Exception as e:
            missing = cid; break
        walked += 1; ps = [str(p) for p in (commit.parents or []) if str(p)]; cid = ps[0] if ps else None
    host_commits = None
    try:
        f = s.fsck(c); fs = {k: (len(v) if isinstance(v, list) else v) for k, v in f.items() if k in ('ok', 'missing', 'corrupt', 'errors')}
    except Exception as e:
        fs = f'{type(e).__name__}: {str(e)[:80]}'
    ok = walked == N + 2 and missing is None
    print(f'  {"✓" if ok else "✗"} N={N:<4} fresh clone walks {walked:>4} of {N + 2} commits; stopped at: {missing[:28] + "…" if missing else "the root"}; fsck: {fs}')
