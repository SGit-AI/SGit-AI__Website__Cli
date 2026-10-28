# Checks three "only sgit" claims against the installed sgit-ai, on its in-memory host:
#   1. `write --also` commits named files to HEAD and leaves other edits uncommitted (a whole-file partial commit)
#   2. a commit that would carry a vault key inside a zip is refused (the secret guard)
#   3. a pull refuses a remote head that does not descend from the one it last accepted (the rewind guard)
import os, sys, io, json, zipfile, tempfile
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup()
S = lambda: Vault__Sync(crypto=Vault__Crypto(), api=api)
W = tempfile.mkdtemp(); d = lambda n: os.path.join(W, n)
def put(base, rel, text):
    p = os.path.join(base, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(text)
out = {'sgit_ai': open(os.path.join(os.path.dirname(__import__('sgit_ai').__file__), 'version')).read().strip()}
s = S(); r = s.init(d('a')); key = r.get('vault_key') or open(os.path.join(d('a'), '.sg_vault/local/vault_key')).read().strip()
for i in range(3): put(d('a'), f'docs/f{i}.md', f'v1 {i}\n')
s.commit(d('a'), message='first'); s.push(d('a'))
# 1. partial commit
put(d('a'), 'docs/f0.md', 'edited, not committed\n'); put(d('a'), 'docs/f1.md', 'edited, not committed\n')
s.write_file(d('a'), 'docs/f2.md', b'written by write\n', 'write one file', also={'docs/new.md': b'and one more\n'})
st = s.status(d('a'))
out['1_write_partial_commit'] = {'still_uncommitted': sorted(st.get('modified', [])), 'clean': st.get('clean')}
# 2. secret guard
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w') as z: z.writestr('backup/VAULT-KEY', key)
open(os.path.join(d('a'), 'docs/holiday-photos.zip'), 'wb').write(buf.getvalue())
try: s.commit(d('a'), message='with a key inside a zip'); out['2_secret_guard'] = 'committed (NOT refused)'
except Exception as e: out['2_secret_guard'] = f'refused: {type(e).__name__}: {str(e)[:140]}'
os.remove(os.path.join(d('a'), 'docs/holiday-photos.zip'))
s.commit(d('a'), message='second'); s.push(d('a'))
# 3. rewind guard
b = S(); b.clone(key, d('b'))
put(d('a'), 'docs/f0.md', 'third\n'); s.commit(d('a'), message='third'); s.push(d('a')); b.pull(d('b'))
target = s.resolve_revision(d('a'), 'HEAD~1'); out['3_reset_to'] = target
s.reset(d('a'), target)
try: s.push(d('a'), force=True); out['3_forced_push'] = 'accepted by the host (it cannot read refs)'
except Exception as e: out['3_forced_push'] = f'{type(e).__name__}: {str(e)[:120]}'
try: b.pull(d('b')); out['3_rewind_guard'] = 'pulled (NOT refused)'
except Exception as e: out['3_rewind_guard'] = f'refused: {type(e).__name__}: {str(e)[:160]}'
print(json.dumps(out, indent=1))
