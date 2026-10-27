# After 0.25.0 created the vault (host.pickle), the new client step by step, verifying the indexes after each.
import os, sys, pickle, json
W = sys.argv[1]
from sgit_ai.core.Vault__Sync import Vault__Sync
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.network.api.Vault__API__In_Memory import Vault__API__In_Memory
from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
from sgit_ai.core.actions.pack.Vault__Pack_Maintain import Vault__Pack_Maintain
api = Vault__API__In_Memory().setup(); api._store, api._tombstones = pickle.load(open(os.path.join(W, 'host.pickle'), 'rb'))
KEY = open(os.path.join(W, 'key.txt')).read().strip(); n = os.path.join(W, 'nn')
s = Vault__Sync(crypto=Vault__Crypto(), api=api); pi = lambda: Vault__Pack_Index(crypto=Vault__Crypto(), api=api)
def check(label):
    v = pi().verify_indexes(n); bad = v['bad']
    print(f'{label}: ok={v["ok"]} packs={v["packs"]} bad={len(bad)}', (bad[0]['pack'].split('/')[-1], bad[0]['error'][:60]) if bad else '')
s.clone(KEY, n); check('after clone')
open(os.path.join(n, 'raw/a/f1.txt'), 'w').write('edited\n'); s.commit(n, message='new'); s.push(n); check('after push')
pi().build_missing(n); check('after build_missing')
Vault__Pack_Maintain(crypto=Vault__Crypto(), api=api).compact(n); check('after compaction')
