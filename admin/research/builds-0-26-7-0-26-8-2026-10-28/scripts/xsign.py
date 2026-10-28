# Cross-version check of 0.26.7's user signatures (design__02): one step per call, on one in-memory host saved to W/host.pickle.
#   python -I xsign.py STEP W [SSH_KEY_PATH]
# Steps: new-create   (the build under test: an unsigned commit, an SSH-signed one, an OpenPGP-signed one; push)
#        old-follow   (any build: clone, log, fsck, verify_signatures, commit, push)
#        new-follow   (the build under test: pull, verify_signatures with user signatures, log lines)
# The CLI of 0.26.8 has no flag that signs, so the signer is handed to Vault__Commit.create_commit, which is what
# the design says commit/write/pull/merge will do.  GNUPGHOME must hold a key with no passphrase for the gpg case.
import os, sys, pickle, json, traceback
STEP, W = sys.argv[1], sys.argv[2]
KEY = sys.argv[3] if len(sys.argv) > 3 else ''
import sgit_ai
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup(); state = os.path.join(W, 'host.pickle')
if os.path.exists(state): api._store, api._tombstones = pickle.load(open(state, 'rb'))
s = Vault__Sync(crypto=Vault__Crypto(), api=api); d = lambda n: os.path.join(W, n)
VER = open(os.path.join(os.path.dirname(sgit_ai.__file__), 'version')).read().strip()
def put(b, r, t):
    p = os.path.join(b, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)
out = {'step': STEP, 'sgit': VER}
def attempt(name, fn):
    try: out[name] = fn()
    except Exception as e: out[name] = f'{type(e).__name__}: {str(e)[:200]}'; traceback.print_exc(file=sys.stderr)
try:
    if STEP == 'new-create':
        from sgit_ai.storage.Vault__Commit import Vault__Commit
        from sgit_ai.crypto.signing.User__Signer import User__Signer
        from sgit_ai.schemas.Schema__Signing_Config import Schema__Signing_Config
        from sgit_ai.safe_types.Enum__User_Signature_Format import Enum__User_Signature_Format as F
        signer = {'none': None,
                  'ssh': User__Signer(config=Schema__Signing_Config(format=F.SSH, signing_key=KEY)),
                  'gpg': User__Signer(config=Schema__Signing_Config(format=F.OPENPGP, signing_key='qa@example.com', gpg_program='gpg'))}
        mode = {'m': 'none'}
        orig = Vault__Commit.create_commit
        def patched(self, *a, **kw):
            kw.setdefault('user_signer', signer[mode['m']]); return orig(self, *a, **kw)
        Vault__Commit.create_commit = patched
        key = s.init(d('n'))['vault_key']; open(d('key.txt'), 'w').write(key)
        for m, f in (('none', 'unsigned.txt'), ('ssh', 'ssh.txt'), ('gpg', 'gpg.txt')):
            mode['m'] = m; put(d('n'), f, f'{m}\n'); s.commit(d('n'), message=f'{m} commit')
        s.push(d('n')); out['pushed'] = 'unsigned, ssh-signed, gpg-signed'
    elif STEP == 'old-follow':
        key = open(d('key.txt')).read().strip(); s.clone(key, d('o'))
        out['files'] = sorted(os.listdir(d('o')))
        attempt('fsck', lambda: {k: v for k, v in s.fsck(d('o')).items() if k in ('ok', 'missing', 'corrupt', 'errors')})
        attempt('verify', lambda: (lambda r: dict(total=r['total'], counts=r['counts']))(s.verify_signatures(d('o'))))
        attempt('log', lambda: [e.get('message') for e in s.log(d('o'))] if hasattr(s, 'log') else 'n/a')
        put(d('o'), 'old.txt', 'from the old client\n')
        attempt('commit+push', lambda: (s.commit(d('o'), message='old client'), s.push(d('o')), 'ok')[2])
    elif STEP == 'new-follow':
        attempt('pull', lambda: (s.pull(d('n')), 'ok')[1])
        out['old.txt'] = os.path.exists(os.path.join(d('n'), 'old.txt'))
        from sgit_ai.core.actions.verify.Vault__User_Signatures import Vault__User_Signatures
        attempt('verify', lambda: (lambda r: dict(total=r['total'], counts=r['counts'], user=r['user_counts']))(
            s.verify_signatures(d('n'), user_signatures=Vault__User_Signatures().setup())))
        attempt('fsck', lambda: {k: v for k, v in s.fsck(d('n')).items() if k in ('ok', 'missing', 'corrupt', 'errors')})
except Exception as e:
    out['error'] = f'{type(e).__name__}: {str(e)[:200]}'; traceback.print_exc(file=sys.stderr)
pickle.dump((api._store, api._tombstones), open(state, 'wb'))
print(json.dumps(out))
