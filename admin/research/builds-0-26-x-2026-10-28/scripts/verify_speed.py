# `pack index verify` on a pack vault of FILES files in FILES/2 folders and PUSHES packs, timed.
#   python -I verify_speed.py FILES PUSHES
import os, sys, tempfile, time
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
FILES, PUSHES = int(sys.argv[1]), int(sys.argv[2])
api = Vault__API__In_Memory().setup(); s = Vault__Sync(crypto=Vault__Crypto(), api=api); a = os.path.join(tempfile.mkdtemp(), 'a')
s.init(a, packs=True)
def put(r, t):
    p = os.path.join(a, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)
for i in range(FILES): put(f'raw/g{i // 200:03d}/f{(i // 2) % 100:03d}/n{i % 2}.txt', f'{i}\n')
s.commit(a, message='first'); s.push(a)
for k in range(PUSHES - 1):
    for j in range(20): put(f'raw/g{(k * 7 + j) % (FILES // 200):03d}/f{j:03d}/n0.txt', f'edit {k} {j}\n')
    s.commit(a, message=f'e{k}'); s.push(a)
t0 = time.time(); v = Vault__Pack_Index(crypto=Vault__Crypto(), api=api).verify_indexes(a); dt = time.time() - t0
print(f'  {FILES:,} files, {PUSHES} packs: verify {dt:.2f} s, ok={v.get("ok")}, packs={v.get("packs")}')
