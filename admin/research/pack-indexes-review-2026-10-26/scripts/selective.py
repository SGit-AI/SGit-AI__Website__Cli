# Two selective-working-copy cases on the in-memory host, with the test suite's own helpers.
import os, sys, json
sys.path.insert(0, sys.argv[1])
from tests._helpers.pack_env import Pack__Env
from tests._helpers.vault_test_env import TEST_VAULT_KEY
FILES = {'raw/uk/gov/a.txt': b'a\n', 'raw/uk/gov/b.txt': b'bb\n', 'raw/fr/edu/c.txt': b'ccc\n', 'top.md': b'# top\n'}
env = Pack__Env(); sync, a, key = env.pack_vault(dict(FILES), vault_key=TEST_VAULT_KEY)

print('== R5: sgit checkout over an uncommitted edit')
sync_b, b = env.clone(key, 'b', no_checkout=True)
sync_b.checkout(b, paths=['raw/uk/gov'])
p = os.path.join(b, 'raw/uk/gov/a.txt'); open(p, 'w').write('MY UNCOMMITTED WORK\n')
print('  status before:', {k: sync_b.status(b)[k] for k in ('modified', 'clean')})
r = sync_b.checkout(b, paths=['raw/uk'])                       # widen to the parent folder
print('  checkout raw/uk wrote:', r['written'])
print('  a.txt now:', open(p).read().strip(), '<- the edit is', 'KEPT' if 'MY UNCOMMITTED' in open(p).read() else 'LOST')

print('== R1: a pack-vault --no-checkout clone whose checkout.json is lost')
sync_c, c = env.clone(key, 'c', no_checkout=True)
sync_c.checkout(c, paths=['top.md'])
os.remove(os.path.join(c, '.sg_vault', 'local', 'checkout.json'))
st = sync_c.status(c); print('  status: deleted =', st['deleted'], ' clean =', st['clean'])
open(os.path.join(c, 'top.md'), 'w').write('# top, edited\n')
try:
    sync_c.commit(c, message='edit top'); sync_c.push(c)
    sync_a2, a2 = env.clone(key, 'a2')
    print('  after commit+push, a fresh clone holds:', sorted(env.tree(a2)))
except Exception as e:
    print('  commit/push raised:', type(e).__name__, str(e)[:120])
