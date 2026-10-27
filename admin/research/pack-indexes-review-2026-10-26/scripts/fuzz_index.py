# Index answers against the walk, under what the branch's own fuzz test leaves out: two writers (three-way merges),
# compaction mid-history, whole-folder deletes, deep adds, duplicate contents. A reader clone pulls incrementally
# through the indexes; after each round its working tree must equal the writer's, and for every commit pack the
# changes and the assembled head map must equal the tree walk.
import os, sys, random, shutil
sys.path.insert(0, sys.argv[1]); SEED = int(sys.argv[2]); ROUNDS = int(sys.argv[3])
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
from sgit_ai.core.actions.pack.Vault__Pack_Index__Reader import Vault__Pack_Index__Reader
from sgit_ai.core.actions.pack.Vault__Pack_Maintain import Vault__Pack_Maintain
from sgit_ai.core.actions.pack.Vault__Packs import PACK_COMMITS
from sgit_ai.storage.Vault__Sub_Tree import Vault__Sub_Tree, FLAT_CACHE
rnd = random.Random(SEED)
FOLDERS = ['raw/uk/gov', 'raw/uk/edu', 'raw/fr/edu', 'raw/fr/gov/old/deep', 'notes', 'raw/de']
env = Pack__Env()
seed_files = {f'{f}/s{i}.txt': f'seed {f} {i}\n'.encode() for f in FOLDERS for i in range(3)}
sync_a, a, key = env.pack_vault(dict(seed_files), vault_key=TEST_VAULT_KEY)
sync_b, b = env.clone(key, 'b'); sync_r, r = env.clone(key, 'r')
def mutate(d, n, tag):
    live = sorted(env.tree(d)); files = {}
    for _ in range(rnd.randint(1, 5)):
        op = rnd.choice(['add', 'add', 'mod', 'mod', 'del', 'rename', 'rmfolder', 'deep', 'dup'])
        if op == 'add' or not live:
            files[f'{rnd.choice(FOLDERS)}/{tag}{n}-{rnd.randint(0, 999)}.txt'] = f'{tag} {n} {rnd.random()}\n'.encode()
        elif op == 'mod':
            p = rnd.choice(live); files[p] = f'mod {tag} {n} {rnd.random()}\n'.encode()
        elif op == 'del':
            p = rnd.choice(live)
            if p not in files and os.path.exists(os.path.join(d, p)): os.remove(os.path.join(d, p))
        elif op == 'rename':
            p = rnd.choice(live)
            if os.path.exists(os.path.join(d, p)):
                data = open(os.path.join(d, p), 'rb').read(); os.remove(os.path.join(d, p)); files[f'{rnd.choice(FOLDERS)}/mv-{tag}{n}.txt'] = data
        elif op == 'rmfolder':
            f = rnd.choice(FOLDERS); full = os.path.join(d, f)
            if os.path.isdir(full): shutil.rmtree(full)
        elif op == 'deep':
            files[f'new/{tag}{n}/a/b/c/leaf.txt'] = f'deep {n}\n'.encode()
        else:
            files[f'{rnd.choice(FOLDERS)}/dup-{tag}{n}.txt'] = b'same bytes everywhere\n'
    env.write(d, files)
def commit_push(sync, d, msg):
    try: sync.commit(d, message=msg)
    except Exception as e:
        if 'nothing to commit' not in str(e): raise
    sync.push(d)
maint = Vault__Pack_Maintain(crypto=sync_a.crypto, api=env.api)
problems = []
for n in range(ROUNDS):
    if rnd.random() < 0.4:                                    # B pushes first; A commits without pulling: a three-way merge
        mutate(b, n, 'b'); commit_push(sync_b, b, f'b {n}')
        mutate(a, n, 'a'); commit_push(sync_a, a, f'a {n}')
        sync_b.pull(b)
    else:
        mutate(a, n, 'a'); commit_push(sync_a, a, f'a {n}'); sync_b.pull(b)
    if rnd.random() < 0.15:
        maint.compact(a)
    sync_a.pull(a); sync_r.pull(r)
    if env.tree(r) != env.tree(a):
        ta, tr = env.tree(a), env.tree(r)
        problems.append(f'round {n}: reader tree differs: only writer {sorted(set(ta)-set(tr))[:3]} only reader {sorted(set(tr)-set(ta))[:3]} '
                        f'content {[p for p in ta if p in tr and ta[p] != tr[p]][:3]}')
# every commit pack: changes and the assembled map against the walk, on the reader clone
c = sync_r._init_components(r); reader = Vault__Pack_Index__Reader(crypto=sync_r.crypto, api=env.api).setup_for(r, c.read_key, c=c)
sg = os.path.join(r, '.sg_vault'); sub = Vault__Sub_Tree(crypto=sync_r.crypto, obj_store=c.obj_store)
checked = 0; gaps = set()
for entry in reader.list_folder(reader._derive_keys_for_directory(r)['vault_id'], PACK_COMMITS) + reader.list_folder(reader._derive_keys_for_directory(r)['vault_id'], 'bare/packs/archive/'):
    cid = entry['commit_id']
    if not c.obj_store.exists(cid): continue
    f = reader.commit_fields(sg, cid, c.read_key)
    if not f['parents']: continue
    parent = reader.commit_fields(sg, f['parents'][0], c.read_key)['tree_id']
    diff = sub.diff_trees(f['tree_id'], parent, c.read_key)
    if not reader.local_index_path(r, cid, 'commit'):
        gaps.add(cid); continue                                          # no index pack here (archived before this clone took it)
    info = reader.changes_of_commit(r, cid, c.read_key)
    if info is None:
        problems.append(f'{cid}: index present but unusable ({reader.notes[-1:] })'); continue
    got = {(x['path'], x['op']) for x in info['changes']}
    want = {(p, 'A') for p in diff['added']} | {(p, 'M') for p in diff['modified']} | {(p, 'D') for p in diff['deleted']}
    if got != want: problems.append(f'{cid}: changes differ from the walk: {sorted(got ^ want)[:4]}')
    FLAT_CACHE.clear(); shutil.rmtree(os.path.join(sg, 'local', 'flat-cache'), ignore_errors=True)
    assembled = reader.seed_head_flat(r, cid, c.read_key, sub)
    dirs = {}; walk = sub._flatten_walk(f['tree_id'], c.read_key, '', dirs=dirs)
    if assembled is None: problems.append(f'{cid}: map not assembled ({reader.notes[-1:]})')
    elif assembled != (walk, dirs): problems.append(f'{cid}: assembled map differs from the walk')
    checked += 1
print(f'seed {SEED}: {ROUNDS} rounds, {checked} commit packs checked, {len(gaps)} without a local index, notes {len(reader.notes)}, problems {len(problems)}')
for p in problems[:8]: print('  ', p)
