import os, sys, pickle, hashlib
W = sys.argv[1]
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
from sgit_ai.storage.Vault__Pack_Store import Vault__Pack_Store
api = Vault__API__In_Memory().setup(); api._store, api._tombstones = pickle.load(open(os.path.join(W, 'host.pickle'), 'rb'))
pi = Vault__Pack_Index(crypto=Vault__Crypto(), api=api); n1 = os.path.join(W, 'n1'); rk = pi._derive_keys_for_directory(n1)['read_key_bytes']
key = lambda part: next(k for k in api._store if part in k)
idx_bytes = api._store[key('indexes/archive/1793064033__obj-cas-imm-babf38668770')]
header = pi.read_header(idx_bytes, rk); print('header data_packs:', header['data_packs'], 'kind:', header['kind'])
member = pi.read_member(idx_bytes, header, 'folder:raw/a', rk)
f0 = member['files']['f0.txt']; print('f0 at:', f0.get('at'), 'blob', f0['blob_id'])
for k in api._store:
    if 'babf38668770' in k and '/indexes/' not in k:
        data = api._store[k]; offs = {o: (a, l) for o, a, l, w in Vault__Pack_Store().member_offsets(data) if not w}
        print(k.split('/bare/packs/')[1], 'len', len(data), 'sha', hashlib.sha256(data).hexdigest()[:12], 'f0 offset in this pack:', offs.get(f0['blob_id']))
print('local data packs n1 knows:', os.listdir(os.path.join(n1, '.sg_vault', 'local')) if False else '')
