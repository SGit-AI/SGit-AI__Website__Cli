# The same ordering, descending only into trees that are in the pack: an unchanged tree holds no new object.
import sys, time, os
from sgit_ai.crypto.Vault__Crypto import Vault__Crypto
from sgit_ai.core.actions.pack.Vault__Pack_Index import Vault__Pack_Index
from sgit_ai.storage.Vault__Object_Store import Vault__Object_Store
from sgit_ai.storage.Vault__Sub_Tree import Vault__Sub_Tree
V = sys.argv[1]; sg = os.path.join(V, '.sg_vault'); pi = Vault__Pack_Index(crypto=Vault__Crypto())
c = pi._init_components(V); rk = c.read_key; lc = pi._read_local_config(V, c.storage)
meta = c.branch_manager.load_branch_index(V, c.branch_index_file_id, rk)
head = c.ref_manager.read_ref(str([b for b in meta.branches if str(b.branch_id) == str(lc.my_branch_id)][0].head_ref_id), rk)
def pruned(self, sg_dir, head_commit_id, read_key, object_ids):
    ids = set(object_ids)
    commits = sorted(c for c in self.reachable_commits(sg_dir, head_commit_id, read_key) if c in ids)
    placed = set(commits); trees, blobs = [], []
    root = str(self._vault_commit(sg_dir).load_commit(head_commit_id, read_key).tree_id or '')
    sub = Vault__Sub_Tree(crypto=self.crypto, obj_store=Vault__Object_Store(vault_path=sg_dir, crypto=self.crypto))
    stack = [root] if root else []
    while stack:
        tid = stack.pop()
        if not tid or tid in placed or tid not in ids:        # the one change: never open a tree that is not in the pack
            continue
        trees.append(tid); placed.add(tid)
        entries = self._entries_or_empty(sub, tid, read_key); children = []
        for name in sorted(entries):
            e = entries[name]
            if e.get('blob_id'):
                bid = str(e['blob_id'])
                if bid in ids and bid not in placed: blobs.append(bid); placed.add(bid)
            elif e.get('tree_id'): children.append(str(e['tree_id']))
        stack.extend(reversed(children))
    return commits + trees + blobs + sorted(ids - placed)
ids = pi.objects_introduced(sg, head, rk)
t = time.perf_counter(); a = pi.path_order(sg, head, rk, ids); ta = time.perf_counter() - t
t = time.perf_counter(); b = pruned(pi, sg, head, rk, ids); tb = time.perf_counter() - t
print(f'branch path_order {ta:.2f} s; pruned {tb:.3f} s; same order: {a == b}; {len(a)} objects')
t = time.perf_counter(); rc = pi.reachable_commits(sg, head, rk); print(f'reachable_commits alone: {time.perf_counter()-t:.3f} s ({len(rc)} commits)')
