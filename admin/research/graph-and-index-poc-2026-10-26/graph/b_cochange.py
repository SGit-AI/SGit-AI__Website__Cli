import os, sys, json, time, sqlite3
S = os.environ['S']; GX = f'{S}/gx'; M = json.load(open(f'{GX}/meta.json')); T = json.load(open(f'{GX}/triples.json'))
# pick the most-changed file so the answer is not trivially small
from collections import Counter, defaultdict
f = Counter(o for s, p, o in T if p == 'changed').most_common(1)[0][0]
def tm(fn, n=50):
    r = fn(); t = time.perf_counter()
    for _ in range(n): r = fn()
    return r, (time.perf_counter() - t) / n * 1e3
out = {}
inc = defaultdict(list); fwd = defaultdict(list)
for s, p, o in T:
    if p == 'changed': inc[o].append(s); fwd[s].append(o)
out['python dicts'] = tm(lambda: len({g for c in inc[f] for g in fwd[c]} - {f}))
db = sqlite3.connect(f'{GX}/triples_text.db')
out['SQLite (SQL self-join)'] = tm(lambda: db.execute("SELECT count(DISTINCT b.o) FROM t a JOIN t b ON b.p='changed' AND b.s=a.s WHERE a.p='changed' AND a.o=? AND b.o<>?", (f, f)).fetchone()[0])
import pyoxigraph as ox
st = ox.Store(f'{GX}/oxi'); E = 'urn:v:'
out['Oxigraph (SPARQL)'] = tm(lambda: int(list(st.query(f'PREFIX p: <{E}p/> SELECT (COUNT(DISTINCT ?g) AS ?n) WHERE {{ ?c p:changed <{E}{f}> . ?c p:changed ?g . FILTER(?g != <{E}{f}>) }}'))[0][0].value))
import real_ladybug as lb
c = lb.Connection(lb.Database(f'{GX}/ladybug.db'))
out['LadybugDB (Cypher)'] = tm(lambda: c.execute('MATCH (x:Node {id:$f})<-[:CHANGED]-(:Commit)-[:CHANGED]->(g:Node) WHERE g.id <> $f RETURN count(DISTINCT g)', {'f': f}).get_next()[0])
import duckdb
d = duckdb.connect(f'{GX}/duck.db', read_only=True)
out['DuckDB (SQL self-join)'] = tm(lambda: d.execute("SELECT count(DISTINCT b.o) FROM t a JOIN t b ON b.p='changed' AND b.s=a.s WHERE a.p='changed' AND a.o=? AND b.o<>?", [f, f]).fetchone()[0])
for k, (v, ms) in out.items(): print(f'  {k:26s} {ms:8.3f} ms  {v}')
json.dump({k: [v, round(ms, 3)] for k, (v, ms) in out.items()}, open(f'{GX}/cochange.json', 'w'))
