import json, zlib, sqlite3, time, hashlib, os, sys
S = sys.argv[1]; FC = f'{S}/bench/v/.sg_vault/local/flat-cache'
heads = {n[:-5]: json.load(open(f'{FC}/{n}')) for n in sorted(os.listdir(FC))}
new = heads['obj-cas-imm-7473af178535']; old = heads['obj-cas-imm-2f25b8d1c74e']
raw = json.dumps(new, separators=(',', ':'), sort_keys=True).encode()
t=time.perf_counter(); z = zlib.compress(raw, 6); tz=time.perf_counter()-t
print(f'flat member: {len(new["flat"])} files, {len(new["dirs"])} folders; json {len(raw)/1e6:.1f} MB, deflated {len(z)/1e6:.2f} MB ({tz:.2f} s)')
t=time.perf_counter(); json.loads(zlib.decompress(z)); print(f'inflate+parse: {time.perf_counter()-t:.2f} s')

def build(path, heads_):
    if os.path.exists(path): os.remove(path)
    db = sqlite3.connect(path)
    db.executescript('''PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA page_size=4096;
      CREATE TABLE flat(tree TEXT, path TEXT, blob TEXT, size INT, hash TEXT, type TEXT, PRIMARY KEY(tree,path)) WITHOUT ROWID;
      CREATE TABLE folders(tree TEXT, path TEXT, child TEXT, PRIMARY KEY(tree,path)) WITHOUT ROWID;''')
    for tid, h in heads_.items():
        db.executemany('INSERT INTO flat VALUES(?,?,?,?,?,?)', ((tid,p,e['blob_id'],e['size'],e['content_hash'],e['content_type']) for p,e in sorted(h['flat'].items())))
        db.executemany('INSERT INTO folders VALUES(?,?,?)', ((tid,p,c) for p,c in sorted(h['dirs'].items())))
    db.commit(); db.execute('VACUUM'); db.close()
t=time.perf_counter(); build(f'{S}/idxexp/a.db', {'new': new}); tb=time.perf_counter()-t
sz=os.path.getsize(f'{S}/idxexp/a.db'); dbz=len(zlib.compress(open(f'{S}/idxexp/a.db','rb').read(),6))
print(f'sqlite assembly, one head: {tb:.2f} s; file {sz/1e6:.1f} MB, deflated {dbz/1e6:.2f} MB')
build(f'{S}/idxexp/b.db', {'new': new})
h=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
print('same bytes twice (same sqlite, same order):', h(f'{S}/idxexp/a.db')==h(f'{S}/idxexp/b.db'))
t=time.perf_counter(); build(f'{S}/idxexp/two.db', {'new': new, 'old': old}); print(f'two heads: {time.perf_counter()-t:.2f} s, {os.path.getsize(f"{S}/idxexp/two.db")/1e6:.1f} MB')
db = sqlite3.connect(f'{S}/idxexp/two.db')
p = next(iter(new['flat']))
def q(label, sql, args=(), n=200):
    t=time.perf_counter()
    for _ in range(n): r = db.execute(sql, args).fetchall()
    print(f'  {label}: {(time.perf_counter()-t)/n*1e3:.3f} ms, {len(r)} rows')
print('queries:')
q('one path', 'SELECT blob,size FROM flat WHERE tree=? AND path=?', ('new', p), 2000)
q('one folder (raw/c09/), prefix range', "SELECT path,blob FROM flat WHERE tree='new' AND path >= 'raw/c09/' AND path < 'raw/c090'", (), 50)
q('diff two heads (changed or added)', "SELECT n.path FROM flat n LEFT JOIN flat o ON o.tree='old' AND o.path=n.path WHERE n.tree='new' AND (o.blob IS NULL OR o.blob<>n.blob)", (), 5)
q('folders whose tree differs', "SELECT n.path FROM folders n LEFT JOIN folders o ON o.tree='old' AND o.path=n.path WHERE n.tree='new' AND (o.child IS NULL OR o.child<>n.child)", (), 5)
q('largest 20 files', "SELECT path,size FROM flat WHERE tree='new' ORDER BY size DESC LIMIT 20", (), 5)
t=time.perf_counter(); blob = db.serialize(); ts=time.perf_counter()-t
t=time.perf_counter(); m = sqlite3.connect(':memory:'); m.deserialize(blob); m.execute('SELECT count(*) FROM flat').fetchone(); td=time.perf_counter()-t
print(f'serialize {len(blob)/1e6:.1f} MB in {ts*1e3:.0f} ms; deserialize into memory {td*1e3:.0f} ms')
t=time.perf_counter(); d = {p:e['blob_id'] for p,e in new['flat'].items()}; dd = [p for p,e in new['flat'].items() if old['flat'].get(p,{}).get('blob_id')!=e['blob_id']]
print(f'python dict diff for comparison: {(time.perf_counter()-t)*1e3:.0f} ms, {len(dd)} rows')
