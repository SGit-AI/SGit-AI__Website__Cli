# Where the time goes on the branch: a --no-checkout clone and history log with the index reader, 76,000 files.
import os, sys, subprocess, cProfile, pstats, io
ROOT = sys.argv[1]; sys.path.insert(0, ROOT)
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
from sgit_ai.objects.Vault__Inspector import Vault__Inspector
from sgit_ai.core.actions.pack.Vault__Pack_Index__Reader import Vault__Pack_Index__Reader
env = Pack__Env(); sync_a = env.sync(); a = env.path('a'); sync_a.init(a, vault_key=TEST_VAULT_KEY, packs=True)
subprocess.run([sys.executable, '-I', os.environ['GENBIG'], a], check=True, capture_output=True)
sync_a.commit(a, message='first'); sync_a.push(a)
files = sorted(os.path.relpath(os.path.join(r, f), a) for r, _, fs in os.walk(a) if '.sg_vault' not in r for f in fs)[:20]
for n in range(3):
    for p in files[n*5:(n+1)*5]: open(os.path.join(a, p), 'a').write(f'x{n}\n')
    sync_a.commit(a, message=f'c{n}'); sync_a.push(a)
def prof(label, fn):
    pr = cProfile.Profile(); pr.enable(); fn(); pr.disable()
    s = io.StringIO(); st = pstats.Stats(pr, stream=s); st.sort_stats('cumulative').print_stats(22)
    print(f'===== {label}'); print('\n'.join(l for l in s.getvalue().splitlines() if l.strip())[:5000])
sync_c = env.sync(); c = env.path('c')
prof('clone --no-checkout', lambda: sync_c.clone(TEST_VAULT_KEY, c, no_checkout=True))
cb = sync_c._init_components(c)
provider = Vault__Pack_Index__Reader(crypto=sync_c.crypto, api=env.api).changes_provider(c, cb.read_key)
print('provider is', 'set' if provider else 'None')
prof('history log, 4 commits, with the index reader', lambda: Vault__Inspector().inspect_commit_chain(c, cb.read_key, limit=10, changes_provider=provider))
