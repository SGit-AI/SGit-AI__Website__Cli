# The pack store under concurrent reads with more packs than MAX_OPEN_PACKS (16): does a read lose its descriptor
# to another thread's eviction? Every error here is a false one: every object is intact on disk.
import io, os, zipfile, random, threading, tempfile, collections
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.storage.Vault__Pack_Store import Vault__Pack_Store
crypto = Vault__Crypto(); base = tempfile.mkdtemp(dir=os.environ['TMPDIR']); sg = os.path.join(base, '.sg_vault'); os.makedirs(sg)
store = Vault__Pack_Store(vault_path=sg, crypto=crypto).setup(create=True)
ids = []
for p in range(24):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_STORED) as z:
        for i in range(50):
            data = os.urandom(2000); oid = 'obj-cas-imm-' + crypto.compute_object_id(data)[len('obj-cas-imm-'):] if crypto.compute_object_id(data).startswith('obj-cas-imm-') else 'obj-cas-imm-' + crypto.compute_object_id(data)
            z.writestr(zipfile.ZipInfo(f'bare/data/{oid}', (1980, 1, 1, 0, 0, 0)), data); ids.append(oid)
    r = store.intake(buf.getvalue(), f'commits/{1700000000 + p}__obj-cas-imm-{p:012x}__{len(buf.getvalue())}.zip')
    assert not r['refused'], r['refused'][:2]
errors = collections.Counter(); ok = [0]; lock = threading.Lock()
def worker(seed):
    rnd = random.Random(seed)
    for _ in range(3000):
        oid = rnd.choice(ids)
        try:
            store.load(oid)
            with lock: ok[0] += 1
        except Exception as e:
            with lock: errors[type(e).__name__ + ': ' + str(e)[:60]] += 1
ts = [threading.Thread(target=worker, args=(s,)) for s in range(8)]
[t.start() for t in ts]; [t.join() for t in ts]
print('reads ok:', ok[0], ' false errors:', sum(errors.values()))
for k, v in errors.most_common(5): print(f'  {v:6d}  {k}')
