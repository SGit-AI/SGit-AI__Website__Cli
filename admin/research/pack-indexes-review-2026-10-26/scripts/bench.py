# End to end on the in-memory host with the 76,000-file vault (vault/genbig.py): the writer's first commit and push,
# clones of each kind, a 300-file pass pushed, pulls, history log, a scoped clone. Run against a repo root; NEW=1
# adds the branch's new modes.
import os, sys, time, json, subprocess, shutil
ROOT = sys.argv[1]; NEW = os.environ.get('NEW') == '1'; sys.path.insert(0, ROOT)
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
from sgit_ai.objects.Vault__Inspector import Vault__Inspector
R = {}
def t(label, fn):
    t0 = time.perf_counter(); out = fn(); R[label] = round(time.perf_counter() - t0, 2); print(f'{label}: {R[label]} s', flush=True); return out
def du(d):
    return round(sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(d) for f in fs) / 1e6, 1)
env = Pack__Env(); sync_a = env.sync(); a = env.path('a'); sync_a.init(a, vault_key=TEST_VAULT_KEY, packs=True)
subprocess.run([sys.executable, '-I', os.environ['GENBIG'], a], check=True, capture_output=True)
t('A commit, 76,000 files', lambda: sync_a.commit(a, message='first'))
t('A first push', lambda: sync_a.push(a))
packs = {k: v for k, v in env.api._store.items() if '/bare/packs/' in k}
R['host packs MB'] = round(sum(len(v) for v in packs.values()) / 1e6, 1)
R['host index packs MB'] = round(sum(len(v) for k, v in packs.items() if '/indexes/' in k) / 1e6, 1)
print('host:', R['host packs MB'], 'MB packs, of which index', R['host index packs MB'], flush=True)
sync_b = env.sync(); b = env.path('b'); t('B clone, full', lambda: sync_b.clone(TEST_VAULT_KEY, b))
R['B .sg_vault MB'] = du(os.path.join(b, '.sg_vault'))
if NEW:
    sync_c = env.sync(); c = env.path('c'); t('C clone --no-checkout', lambda: sync_c.clone(TEST_VAULT_KEY, c, no_checkout=True))
    sync_d = env.sync(); d = env.path('d'); t('D clone --pack-store', lambda: sync_d.clone(TEST_VAULT_KEY, d, pack_store=True))
    R['D .sg_vault MB'] = du(os.path.join(d, '.sg_vault'))
sync_e = env.sync(); e = env.path('e'); env.api.reset_counts()
t('E clone --path raw/c09/s4', lambda: sync_e.clone(TEST_VAULT_KEY, e, scope_paths=['raw/c09/s4']))
R['E requests'] = env.api.requests(); R['E range MB'] = round(getattr(env.api, 'range_bytes', 0) / 1e6, 2)
vid = next(iter(env.api._store)).split('/')[0]
whole = [f for f in env.api.requested_ids if f not in {x[0] for x in getattr(env.api, 'range_reads', [])}]
R['E whole-file MB'] = round(sum(len(env.api._store.get(f'{vid}/{f}', b'') or b'') for f in whole) / 1e6, 2)
R['E files in scope'] = sum(1 for r, _, fs in os.walk(e) if '.sg_vault' not in r for f in fs)
# a pass: 300 files changed in one folder group, then a 5-file commit
files = sorted(p for p in (os.path.relpath(os.path.join(r, f), a) for r, _, fs in os.walk(a) if '.sg_vault' not in r for f in fs) if p.startswith('raw/c03/s1/'))[:300]
for i, p in enumerate(files): open(os.path.join(a, p), 'a').write(f'pass {i}\n')
t('A commit, a 300-file pass', lambda: sync_a.commit(a, message='pass'))
t('A push of the pass', lambda: sync_a.push(a))
for i, p in enumerate(files[:5]): open(os.path.join(a, p), 'a').write(f'small {i}\n')
sync_a.commit(a, message='small'); t('A push of a 5-file commit', lambda: sync_a.push(a))
t('B pull of both', lambda: sync_b.pull(b))
if NEW:
    t('C pull --no-checkout', lambda: sync_c.pull(c, checkout=False))
    t('D pull (pack store)', lambda: sync_d.pull(d))
cb = sync_b._init_components(b)
provider = None
if NEW:
    from sgit_ai.core.actions.pack.Vault__Pack_Index__Reader import Vault__Pack_Index__Reader
    provider = Vault__Pack_Index__Reader(crypto=sync_b.crypto, api=env.api).changes_provider(b, cb.read_key)
t('history log, 3 commits with counts', lambda: Vault__Inspector().inspect_commit_chain(b, cb.read_key, limit=10, changes_provider=provider) if NEW
                                         else Vault__Inspector().inspect_commit_chain(b, cb.read_key, limit=10))
if NEW:
    from sgit_ai.core.actions.pack.Vault__Pack_Maintain import Vault__Pack_Maintain
    t('A compact', lambda: Vault__Pack_Maintain(crypto=sync_a.crypto, api=env.api).compact(a))
    sync_f = env.sync(); f = env.path('f'); t('F clone after compaction', lambda: sync_f.clone(TEST_VAULT_KEY, f, no_checkout=True))
    cf = sync_f._init_components(f)
    pf = Vault__Pack_Index__Reader(crypto=sync_f.crypto, api=env.api).changes_provider(f, cf.read_key)
    t('history log after compaction, fresh clone', lambda: Vault__Inspector().inspect_commit_chain(f, cf.read_key, limit=10, changes_provider=pf))
print(json.dumps(R)); json.dump(R, open(os.environ['OUT'], 'w'), indent=1)
