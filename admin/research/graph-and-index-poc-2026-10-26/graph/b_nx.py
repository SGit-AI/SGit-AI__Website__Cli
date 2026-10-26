from common import *
import networkx as nx
t = time.perf_counter()
tree = nx.DiGraph(); dag = nx.DiGraph(); rest = nx.MultiDiGraph(); ts = {}
for s, p, o in T:
    if p == 'contains': tree.add_edge(s, o)
    elif p == 'parent': dag.add_edge(o, s)            # parent -> child, the orientation nx's DAG algorithms expect
    elif p == 'ts': ts[s] = int(o)
    elif p in ('changed', 'blob'): rest.add_edge(s, o, p=p)
load = time.perf_counter() - t
R = {}
R['children']          = timed(lambda: tree.out_degree(f'd:{M["folder_deep"]}'))
R['subtree_files']     = timed(lambda: sum(1 for n in nx.descendants(tree, f'd:{M["folder"]}') if n.startswith('f:')))
R['file_to_root']      = timed(lambda: len(nx.ancestors(tree, f'f:{M["file"]}')))
R['ancestors_of_head'] = timed(lambda: len(nx.ancestors(dag, M['head'])))
R['merge_base']        = timed(lambda: nx.lowest_common_ancestor(dag, M['head'], M['side_tip']))
R['base_to_head']      = timed(lambda: len((nx.ancestors(dag, M['head']) | {M['head']}) - (nx.ancestors(dag, M['base']) | {M['base']})))
R['file_history']      = timed(lambda: sum(1 for u, v, d in rest.in_edges(f'f:{M["file"]}', data=True) if d['p'] == 'changed'))
R['paths_of_blob']     = timed(lambda: rest.in_degree(M['blob']))
report(f'networkx {nx.__version__} (pure Python, in memory)', load, None, R)
