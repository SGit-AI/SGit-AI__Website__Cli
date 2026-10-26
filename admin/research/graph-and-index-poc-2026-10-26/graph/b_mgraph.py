import time, sys
from mgraph_db.mgraph.MGraph import MGraph
for n in (1000, 5000):
    g = MGraph(); t = time.perf_counter()
    with g.edit() as e:
        prev = e.new_node()
        for i in range(n):
            node = e.new_node()
            e.new_edge(from_node_id=node.node_id, to_node_id=prev.node_id)
            prev = node
    el = time.perf_counter() - t
    print(f'MGraph-DB: {n} nodes + {n} edges in {el:.2f} s ({el/n*1e6:.0f} us per node+edge)')
# a walk: follow outgoing edges from the last node to the first
idx = g.edit().index()
t = time.perf_counter(); x = prev.node_id; steps = 0
while True:
    nxt = idx.nodes_ids__from__node_id(x)
    if not nxt: break
    x = nxt[0]; steps += 1
print(f'walk of {steps} hops: {(time.perf_counter()-t)*1e3:.1f} ms')
