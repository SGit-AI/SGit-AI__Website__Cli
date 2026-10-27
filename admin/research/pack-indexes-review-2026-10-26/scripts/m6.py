# M6: after compaction, does a fresh clone's history log find every commit's changes from an index (archived ones
# fetched on demand), walking trees only for the root?
import os, sys
sys.path.insert(0, sys.argv[1])
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
from sgit_ai.core.actions.pack.Vault__Pack_Maintain import Vault__Pack_Maintain
from sgit_ai.core.actions.pack.Vault__Pack_Index__Reader import Vault__Pack_Index__Reader
from sgit_ai.objects.Vault__Inspector import Vault__Inspector
env = Pack__Env(); sync, a, key = env.pack_vault({f'd{i}/f.txt': f'{i}\n' for i in range(20)}, vault_key=TEST_VAULT_KEY)
for n in range(12):
    env.write(a, {f'd{n}/f.txt': f'edit {n}\n'}); sync.commit(a, message=f'c{n}'); sync.push(a)
Vault__Pack_Maintain(crypto=sync.crypto, api=env.api).compact(a)
env.write(a, {'d0/after.txt': 'after\n'}); sync.commit(a, message='after compaction'); sync.push(a)
sync_f, f = env.clone(key, 'f', no_checkout=True); c = sync_f._init_components(f)
provider = Vault__Pack_Index__Reader(crypto=sync_f.crypto, api=env.api).changes_provider(f, c.read_key, c=c)
import time; t0 = time.perf_counter()
chain = Vault__Inspector().inspect_commit_chain(f, c.read_key, limit=20, changes_provider=provider)
print(f'log with the provider: {time.perf_counter()-t0:.2f} s')
hits = [e['commit_id'] for e in chain if provider(e['commit_id']) is not None]
miss = [e.get('message') for e in chain if provider(e['commit_id']) is None]
print(f'{len(chain)} commits in the log; changes from an index for {len(hits)}; walked for: {miss}')
