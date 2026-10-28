# 0.26.10+: signing on every path the CLI team lists: commit, write, tag, a merge made by pull, revert --as-commit.
# Library calls with Schema__Signing_Flags (what -S / -s become), on the in-memory host; then each object's user signature is checked.
#   GIT_CONFIG_GLOBAL=/dev/null python -I signing_paths.py SSH_KEY_PATH
import os, sys, tempfile
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.schemas.Schema__Signing_Flags import Schema__Signing_Flags
from sgit_ai.safe_types.Enum__Sign_Choice import Enum__Sign_Choice
from sgit_ai.core.actions.verify.Vault__User_Signatures import Vault__User_Signatures
KEY = sys.argv[1]; W = tempfile.mkdtemp()
ON = Schema__Signing_Flags(sign=Enum__Sign_Choice.ON, key=KEY)
api = Vault__API__In_Memory().setup(); s = Vault__Sync(crypto=Vault__Crypto(), api=api); a, b = os.path.join(W, 'a'), os.path.join(W, 'b')
def put(d, r, t): open(os.path.join(d, r), 'w').write(t)
key = s.init(a)['vault_key']; put(a, 'x.txt', 'x\n'); put(a, 'y.txt', 'y\n'); s.commit(a, message='unsigned base'); s.push(a)
s.clone(key, b)
def users(d): return {k: v for k, v in s.verify_signatures(d, user_signatures=Vault__User_Signatures().setup())['user_counts'].items() if v}
put(a, 'x.txt', 'x2\n'); s.commit(a, message='signed commit', signing=ON); print('commit        ', users(a))
r = s.write_file(a, 'w.txt', b'written\n', message='signed write', signing=ON); print('write         ', users(a))
s.push(a); t = s.tag_create(a, 'v1', message='signed tag', signing=ON); sh = s.tag_show(a, 'v1'); print('tag           ', t.get('signed_with', '')[:40], '| tag_show user_signature:', (sh.get('user_signature') or {}).get('status'))
s.push(a)
put(b, 'y.txt', 'y-from-b\n'); s.commit(b, message='b local commit (unsigned)')
s.pull(b, signing=ON) if 'signing' in s.pull.__code__.co_varnames else s.pull(b); print('merge by pull ', users(b), '(counts all commits reachable: unsigned base, b local, signed ones, merge)')
head = s.resolve_revision(b, 'HEAD'); put(b, 'z.txt', 'z\n'); s.commit(b, message='to revert'); rev = s.resolve_revision(b, 'HEAD')
before = users(b); s.revert_commit(b, rev, message='signed revert', signing=ON); print('revert        ', before, '->', users(b))
