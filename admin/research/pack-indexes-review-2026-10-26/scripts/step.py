# One step of the cross-version check: load the in-memory host from disk, act as this Python's sgit, save it back.
# Every host call is logged with the prefix or file id asked for.
import os, sys, pickle, json
STEP, W = sys.argv[1], sys.argv[2]
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.core.actions.pack.Vault__Pack_Maintain import Vault__Pack_Maintain
class Host(Vault__API__In_Memory):
    def setup(self):
        super().setup(); self.log = []; return self
    def list_files(self, vault_id, prefix=''):
        self.log.append(('list', prefix)); return super().list_files(vault_id, prefix)
    def batch_read(self, vault_id, file_ids, failures=None):
        self.log.extend(('read', f) for f in file_ids); return super().batch_read(vault_id, file_ids, failures=failures)
    def read(self, vault_id, file_id):
        self.log.append(('read', file_id)); return super().read(vault_id, file_id)
api = Host().setup()
state = os.path.join(W, 'host.pickle')
if os.path.exists(state):
    with open(state, 'rb') as f: api._store, api._tombstones = pickle.load(f)
sync = lambda: Vault__Sync(crypto=Vault__Crypto(), api=api)
KEY = open(os.path.join(W, 'key.txt')).read().strip()
d = lambda n: os.path.join(W, n)
def write(directory, files):
    for rel, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(directory, rel)), exist_ok=True); open(os.path.join(directory, rel), 'w').write(text)
def tree(directory):
    out = {}
    for r, ds, fs in os.walk(directory):
        ds[:] = [x for x in ds if x != '.sg_vault']
        for f in fs: out[os.path.relpath(os.path.join(r, f), directory)] = open(os.path.join(r, f)).read()
    return out
out = {}
if STEP == 'new-create':
    s = sync(); s.init(d('n1'), vault_key=KEY, packs=True)
    write(d('n1'), {f'raw/a/f{i}.txt': f'file {i}\n' for i in range(30)} | {f'raw/b/g{i}.txt': f'b {i}\n' for i in range(30)})
    s.commit(d('n1'), message='first'); s.push(d('n1'))
    write(d('n1'), {'raw/a/f1.txt': 'file 1 edited\n', 'raw/b/new.txt': 'new\n'}); s.commit(d('n1'), message='second'); s.push(d('n1'))
elif STEP == 'old-create':
    s = sync(); s.init(d('o1'), vault_key=KEY, packs=True)
    write(d('o1'), {f'raw/a/f{i}.txt': f'file {i}\n' for i in range(30)} | {f'raw/b/g{i}.txt': f'b {i}\n' for i in range(30)})
    s.commit(d('o1'), message='first, by 0.25.0'); s.push(d('o1'))
elif STEP == 'new-join':
    s = sync(); s.clone(KEY, d('n1')); out['clone_equal'] = tree(d('n1')) == tree(d('o1'))
    write(d('n1'), {'raw/a/f1.txt': 'edited by the new client\n', 'raw/c/new.txt': 'new\n'}); s.commit(d('n1'), message='new client'); s.push(d('n1'))
    from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
    pi = Vault__Pack_Index(crypto=Vault__Crypto(), api=api); vid = pi._derive_keys_for_directory(d('n1'))['vault_id']
    out['index_packs_on_host'] = sum(1 for k in api._store if '/bare/packs/indexes/' in k)
    pi.build_missing(d('n1')); out['index_packs_after_build'] = sum(1 for k in api._store if '/bare/packs/indexes/' in k)
    Vault__Pack_Maintain(crypto=Vault__Crypto(), api=api).compact(d('n1'))
    from sgit_ai.storage.Vault__Format import Vault__Format
    c = s._init_components(d('n1')); idx = c.branch_manager.load_branch_index(d('n1'), c.branch_index_file_id, c.read_key)
    out['min_client'] = Vault__Format().min_client_of(idx); out['features'] = Vault__Format().features_of(idx)
elif STEP == 'new-verify':
    from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
    pi = Vault__Pack_Index(crypto=Vault__Crypto(), api=api)
    v = pi.verify_indexes(d('n1'))
    out['report'] = {k: (v[k] if not isinstance(v[k], list) else v[k][:6]) for k in v}
    out['host_index_packs'] = sorted(k.split('/bare/packs/indexes/')[1] for k in api._store if '/bare/packs/indexes/' in k)
    out['host_data_packs'] = sorted(k.split('/bare/packs/')[1] for k in api._store if '/bare/packs/' in k and '/indexes/' not in k)
elif STEP == 'old-work':
    s = sync(); s.clone(KEY, d('o1')); out['clone_equal'] = tree(d('o1')) == tree(d('n1'))
    write(d('o1'), {'raw/a/f2.txt': 'edited by 0.25.0\n', 'raw/c/h.txt': 'from the old client\n'}); s.commit(d('o1'), message='old client'); s.push(d('o1'))
    m = Vault__Pack_Maintain(crypto=Vault__Crypto(), api=api)
    out['verify_ok'] = m.verify(d('o1'))['ok']
    out['compact'] = {k: v for k, v in m.compact(d('o1')).items() if isinstance(v, (int, str, bool))}
elif STEP == 'new-follow':
    s = sync(); r = s.pull(d('n1')); out['pull'] = r.get('status')
    out['n1_equals_o1'] = tree(d('n1')) == tree(d('o1'))
    s2 = sync(); s2.clone(KEY, d('n2')); out['n2_equals_o1'] = tree(d('n2')) == tree(d('o1'))
    from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
    pi = Vault__Pack_Index(crypto=Vault__Crypto(), api=api)
    out['missing_before'] = len(pi.data_packs_without_index(pi._derive_keys_for_directory(d('n1'))['vault_id']))
    b = pi.build_missing(d('n1')); out['build'] = {k: v for k, v in b.items() if isinstance(v, (int, str))}
    v = pi.verify_indexes(d('n1')); out['verify_indexes_ok'] = v.get('ok')
    write(d('n1'), {'raw/b/g3.txt': 'new client again\n'}); s.commit(d('n1'), message='new again'); s.push(d('n1'))
    Vault__Pack_Maintain(crypto=Vault__Crypto(), api=api).compact(d('n1'))
elif STEP == 'old-follow':
    s = sync(); out['pull'] = s.pull(d('o1')).get('status'); out['o1_equals_n1'] = tree(d('o1')) == tree(d('n1'))
    s2 = sync(); s2.clone(KEY, d('o2')); out['o2_equals_n1'] = tree(d('o2')) == tree(d('n1'))
    out['verify_ok'] = Vault__Pack_Maintain(crypto=Vault__Crypto(), api=api).verify(d('o2'))['ok']
idx = [x for x in api.log if 'indexes' in x[1]]
out['host_calls'] = len(api.log); out['calls_under_indexes'] = idx[:5]; out['n_calls_under_indexes'] = len(idx)
with open(state, 'wb') as f: pickle.dump((api._store, api._tombstones), f)
print(STEP, json.dumps(out))
