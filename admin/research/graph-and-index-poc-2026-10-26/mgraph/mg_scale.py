# MGraph-DB at scale: generate its JSON directly (a chain plus a tree, with predicates), then time the typed load,
# the index build, the index's own JSON round trip, and plain json.loads as the floor.
import json, time, sys, os, gc, resource
from mgraph_db.mgraph.schemas.Schema__MGraph__Graph import Schema__MGraph__Graph
from mgraph_db.mgraph.index.MGraph__Index import MGraph__Index
EDGE = 'mgraph_db.mgraph.schemas.Schema__MGraph__Edge.Schema__MGraph__Edge'
def make(n):
    nodes = {}; edges = {}
    hx = lambda i: f'{i:08x}'
    for i in range(n): nodes[hx(i)] = dict(node_data=None, node_path=None, node_type=None, node_id=hx(i))
    for i in range(1, n):
        e = f'e{i:07x}'
        edges[e] = dict(edge_data=None, edge_type=EDGE, edge_label=dict(incoming=None, outgoing=None, predicate='parent' if i % 2 else 'contains'),
                        edge_path=None, from_node_id=hx(i), to_node_id=hx(i - 1 if i % 2 else i // 2), edge_id=e)
    return dict(graph_data=None, graph_path=None, graph_type=None, schema_types=None, index_config=None, edges=edges, graph_id='abcdef01', nodes=nodes)
from osbot_utils.type_safe.type_safe_core.config.Type_Safe__Config import Type_Safe__Config
import contextlib
FAST = os.environ.get('FAST') == '1'
ctx = (lambda: Type_Safe__Config(fast_create=True, skip_validation=True)) if FAST else contextlib.nullcontext
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
for n in [int(x) for x in sys.argv[1:]]:
    d = make(n); raw = json.dumps(d).encode(); gc.collect()
    t = time.perf_counter(); json.loads(raw); tj = time.perf_counter() - t
    with ctx():
        t = time.perf_counter(); g = Schema__MGraph__Graph.from_json(json.loads(raw)); tl = time.perf_counter() - t
        t = time.perf_counter(); idx = MGraph__Index.from_graph(g); ti = time.perf_counter() - t
    t = time.perf_counter(); ij = idx.index_data.json(); traw = json.dumps(ij, default=str).encode(); ts = time.perf_counter() - t
    from mgraph_db.mgraph.schemas.index.Schema__MGraph__Index__Data import Schema__MGraph__Index__Data
    with ctx():
        t = time.perf_counter(); Schema__MGraph__Index__Data.from_json(json.loads(traw)); tr = time.perf_counter() - t
    # a query on the index: walk the parent chain from the last node
    t = time.perf_counter(); x = f'{(n-1) if (n-1) % 2 else n-2:08x}'; hops = 0
    out = idx.index_data.edges.nodes_to_outgoing_edges; e2n = idx.index_data.edges.edges_to_nodes
    while True:
        es = out.get(x)
        if not es: break
        x = e2n[next(iter(es))][1]; hops += 1
    tw = time.perf_counter() - t
    print(json.dumps(dict(fast=FAST, nodes=n, edges=n - 1, graph_json_mb=round(len(raw)/1e6, 1), json_loads_s=round(tj, 2), typed_load_s=round(tl, 2),
          index_build_s=round(ti, 2), index_json_mb=round(len(traw)/1e6, 1), index_save_s=round(ts, 2), index_typed_reload_s=round(tr, 2),
          walk_hops=hops, walk_ms=round(tw*1e3, 1), max_rss_mb=round(rss()))), flush=True)
    del d, raw, g, idx, ij, traw; gc.collect()
