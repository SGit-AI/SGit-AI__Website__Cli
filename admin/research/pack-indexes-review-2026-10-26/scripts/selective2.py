import os, sys
sys.path.insert(0, sys.argv[1])
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
FILES = {'raw/uk/gov/a.txt': b'a\n', 'raw/uk/gov/b.txt': b'bb\n', 'raw/fr/edu/c.txt': b'ccc\n', 'top.md': b'# top\n'}
env = Pack__Env(); sync, a, key = env.pack_vault(dict(FILES), vault_key=TEST_VAULT_KEY)
sync_c, c = env.clone(key, 'c', no_checkout=True)
sync_c.checkout(c, paths=['top.md'])
os.remove(os.path.join(c, '.sg_vault', 'local', 'checkout.json'))
open(os.path.join(c, 'top.md'), 'w').write('# top, edited\n')
r = sync_c.commit(c, message='edit top'); print('commit 1:', {k: r.get(k) for k in ('files_changed', 'commit_id') if k in r})
flat = sync_c._get_head_flat_map(c)[0]; print('local head holds:', sorted(flat))
for attempt in (2, 3):
    try:
        sync_c.push(c); print(f'push {attempt-1}: ok'); break
    except Exception as e:
        print(f'push {attempt-1} refused:', str(e)[:70])
        try:
            r = sync_c.commit(c, message='again'); print(f'commit {attempt}:', r.get('files_changed'), 'head holds', sorted(sync_c._get_head_flat_map(c)[0]))
        except Exception as e2:
            print(f'commit {attempt} raised:', str(e2)[:90])
