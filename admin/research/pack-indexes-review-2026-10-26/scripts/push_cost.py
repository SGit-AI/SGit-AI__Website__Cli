# The per-push work this branch adds, on the 76,000-file benchmark vault (objects loose): path_order of the head
# commit's own objects (what build_commit_pack does), and the index members of that commit (build_commit_members).
import sys, time, os
from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
from sgit_ai.storage.Vault__Sub_Tree import FLAT_CACHE
V = sys.argv[1]; sg = os.path.join(V, '.sg_vault')
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
pi = Vault__Pack_Index(crypto=Vault__Crypto())
c = pi._init_components(V); rk = c.read_key
head = c.ref_manager.read_ref(c.branch_manager.get_branch_by_id(V, c.branch_index_file_id, c.read_key, None) if False else None, rk) if False else None
from sgit_ai.storage.Vault__Ref_Manager import Vault__Ref_Manager
lc = pi._read_local_config(V, c.storage)
meta = c.branch_manager.load_branch_index(V, c.branch_index_file_id, rk)
br = [b for b in meta.branches if str(b.branch_id) == str(lc.my_branch_id)][0]
head = c.ref_manager.read_ref(str(br.head_ref_id), rk)
print('head', head)
t = time.perf_counter(); ids = pi.objects_introduced(sg, head, rk); print(f'objects_introduced: {len(ids)} ids, {time.perf_counter()-t:.2f} s')
t = time.perf_counter(); order = pi.path_order(sg, head, rk, ids); print(f'path_order (per commit pack): {time.perf_counter()-t:.2f} s')
FLAT_CACHE.clear()
t = time.perf_counter(); fields, members = pi.build_commit_members(sg, head, rk); print(f'build_commit_members: {len(members)} members, {time.perf_counter()-t:.2f} s (flat cache on disk, process cache cold)')
t = time.perf_counter(); fields, members = pi.build_commit_members(sg, head, rk); print(f'build_commit_members again: {time.perf_counter()-t:.2f} s (process cache warm)')
