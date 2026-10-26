from common import *
import csv, shutil, zlib, importlib, signal
which = sys.argv[1]                                       # ladybug | kuzu
mod = importlib.import_module('real_ladybug' if which == 'ladybug' else 'kuzu')
path = f'{GX}/{which}.db'; shutil.rmtree(path, ignore_errors=True)
if os.path.exists(path): os.remove(path)
csvd = f'{GX}/csv'; os.makedirs(csvd, exist_ok=True)
def w(name, rows):
    with open(f'{csvd}/{name}.csv', 'w', newline='') as f: csv.writer(f).writerows(rows)
nodes = {}; files = {}; commits = {}; blobs = set()
for s, p, o in T:
    if p == 'contains': nodes.setdefault(s, 'd'); nodes[o] = 'f' if o.startswith('f:') else 'd'
    elif p == 'ts': commits[s] = o
    elif p == 'blob': blobs.add(o)
t = time.perf_counter()
w('node', [(k, v) for k, v in nodes.items()]); w('commit', [(k, v) for k, v in commits.items()]); w('blob', [(b,) for b in blobs])
w('contains', [(s, o) for s, p, o in T if p == 'contains']); w('parent', [(s, o) for s, p, o in T if p == 'parent'])
w('changed', [(s, o) for s, p, o in T if p == 'changed']); w('has_blob', [(s, o) for s, p, o in T if p == 'blob'])
db = mod.Database(path); c = mod.Connection(db)
for q in ['CREATE NODE TABLE Node(id STRING, kind STRING, PRIMARY KEY(id))', 'CREATE NODE TABLE Commit(id STRING, ts INT64, PRIMARY KEY(id))',
          'CREATE NODE TABLE Blob(id STRING, PRIMARY KEY(id))', 'CREATE REL TABLE CONTAINS(FROM Node TO Node)', 'CREATE REL TABLE PARENT(FROM Commit TO Commit)',
          'CREATE REL TABLE CHANGED(FROM Commit TO Node)', 'CREATE REL TABLE HAS_BLOB(FROM Node TO Blob)']: c.execute(q)
for tbl, f in [('Node', 'node'), ('Commit', 'commit'), ('Blob', 'blob'), ('CONTAINS', 'contains'), ('PARENT', 'parent'), ('CHANGED', 'changed'), ('HAS_BLOB', 'has_blob')]:
    c.execute(f'COPY {tbl} FROM "{csvd}/{f}.csv" (HEADER=false)')
load = time.perf_counter() - t
c.execute("CALL var_length_extend_max_depth=30000")
size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs) if os.path.isdir(path) else os.path.getsize(path)
def val(q, **p):
    r = c.execute(q, p); return r.get_next()[0]
class TO(Exception): pass
def _alarm(*a): raise TO()
signal.signal(signal.SIGALRM, _alarm)
_timed = timed
def timed(fn, n=None):
    signal.alarm(60)
    try: return _timed(fn, n)
    except TO: print('    .. over 60 s'); return ('timeout', 60.0)
    except Exception as e: print('    .. error', str(e)[:200]); return ('error', 0)
    finally: signal.alarm(0)
D = 30000
R = {}
R['children']          = timed(lambda: val('MATCH (d:Node {id:$x})-[:CONTAINS]->(k) RETURN count(k)', x=f'd:{M["folder_deep"]}'))
R['subtree_files']     = timed(lambda: val("MATCH (d:Node {id:$x})-[:CONTAINS*1..12]->(f:Node) WHERE f.kind='f' RETURN count(f)", x=f'd:{M["folder"]}'))
R['file_to_root']      = timed(lambda: val('MATCH (d:Node)-[:CONTAINS*1..12]->(f:Node {id:$x}) RETURN count(d)', x=f'f:{M["file"]}'))
R['ancestors_of_head'] = timed(lambda: val(f'MATCH (h:Commit {{id:$x}})-[:PARENT* SHORTEST 1..{D}]->(a:Commit) RETURN count(DISTINCT a)', x=M['head']))
R['merge_base']        = timed(lambda: val(f'''MATCH (h:Commit {{id:$a}})-[:PARENT* SHORTEST 1..{D}]->(x:Commit) WITH collect(x.id) + [$a] AS A
    MATCH (s:Commit {{id:$b}})-[:PARENT* SHORTEST 1..{D}]->(y:Commit) WHERE list_contains(A, y.id) RETURN y.id ORDER BY y.ts DESC LIMIT 1''', a=M['head'], b=M['side_tip']))
R['base_to_head']      = timed(lambda: val(f'''MATCH (b:Commit {{id:$b}})-[:PARENT* SHORTEST 1..{D}]->(x:Commit) WITH collect(x.id) + [$b] AS B
    MATCH (h:Commit {{id:$h}})-[:PARENT* SHORTEST 1..{D}]->(y:Commit) WHERE NOT list_contains(B, y.id) RETURN count(y) + 1''', b=M['base'], h=M['head']))
R['file_history']      = timed(lambda: val('MATCH (c:Commit)-[:CHANGED]->(f:Node {id:$x}) RETURN count(c)', x=f'f:{M["file"]}'))
R['paths_of_blob']     = timed(lambda: val('MATCH (f:Node)-[:HAS_BLOB]->(b:Blob {id:$x}) RETURN count(f)', x=M['blob']))
names = {'ladybug': f'LadybugDB {mod.__version__}, Cypher (Kuzu fork, C++ wheel)', 'kuzu': f'Kuzu {mod.__version__}, Cypher (archived Oct 2025)'}
report(names[which], load, size, R)
