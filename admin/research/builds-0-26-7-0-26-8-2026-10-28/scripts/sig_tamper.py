# 0.26.7+: a user signature made over other bytes, and one with a corrupt blob, must verify as "bad"; a good one as good/untrusted.
#   python -I sig_tamper.py SSH_KEY_PATH W
import os, sys, tempfile, base64
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.storage.Vault__Commit import Vault__Commit
from sgit_ai.crypto.signing.User__Signer import User__Signer
from sgit_ai.schemas.Schema__Signing_Config import Schema__Signing_Config
from sgit_ai.safe_types.Enum__User_Signature_Format import Enum__User_Signature_Format as F
from sgit_ai.core.actions.verify.Vault__User_Signatures import Vault__User_Signatures
KEY = sys.argv[1]; d = os.path.join(tempfile.mkdtemp(), 'v')
s = Vault__Sync(crypto=Vault__Crypto(), api=Vault__API__In_Memory().setup()); s.init(d)
real = User__Signer(config=Schema__Signing_Config(format=F.SSH, signing_key=KEY))
class Wrong(User__Signer):
    def sign(self, payload): return real.sign(payload + b'x')
class Corrupt(User__Signer):
    def sign(self, payload):
        sig = real.sign(payload); raw = bytearray(base64.b64decode(str(sig.blob))); raw[-5] ^= 1
        sig.blob = base64.b64encode(bytes(raw)).decode(); return sig
mode = {'m': real}; orig = Vault__Commit.create_commit
Vault__Commit.create_commit = lambda self, *a, **kw: orig(self, *a, **{**kw, 'user_signer': mode['m']})
for name, m in (('good', real), ('signed-other-bytes', Wrong(config=real.config)), ('corrupt-blob', Corrupt(config=real.config))):
    mode['m'] = m; open(os.path.join(d, name), 'w').write(name); s.commit(d, message=name)
r = s.verify_signatures(d, user_signatures=Vault__User_Signatures().setup())
print('clone signatures:', r['counts']); print('user signatures :', {k: v for k, v in r['user_counts'].items() if v})
