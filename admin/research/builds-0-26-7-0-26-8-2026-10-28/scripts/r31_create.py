import os, sys, pickle
W = sys.argv[1]; os.makedirs(W, exist_ok=True)
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
api = Vault__API__In_Memory().setup(); s = Vault__Sync(crypto=Vault__Crypto(), api=api); o = os.path.join(W, 'o1')
key = s.init(o, packs=True)['vault_key']; open(os.path.join(W, 'key.txt'), 'w').write(key)
for d, n in (('a', 'f'), ('b', 'g')):
    os.makedirs(os.path.join(o, 'raw', d), exist_ok=True)
    for i in range(30): open(os.path.join(o, 'raw', d, f'{n}{i}.txt'), 'w').write(f'file {i}\n')
s.commit(o, message='first, by 0.25.0'); s.push(o)
pickle.dump((api._store, api._tombstones), open(os.path.join(W, 'host.pickle'), 'wb'))
