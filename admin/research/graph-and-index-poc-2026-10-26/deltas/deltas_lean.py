# The lean delta: the folder files on the changed paths (whole, they are small) plus one 'changes' record per commit
# (path, old blob, new blob). No cross-reference shards travel; the reader applies the changes to its own.
import json, zlib, time, os, hashlib, random
from collections import defaultdict
S = os.environ['S']; head = json.load(open(f'{S}/bench/v/.sg_vault/local/flat-cache/obj-cas-imm-7473af178535.json'))
pj = lambda o: zlib.compress(json.dumps(o, separators=(',', ':'), sort_keys=True).encode(), 6)
uj = lambda b: json.loads(zlib.decompress(b))
key = lambda d: f'folders/{hashlib.sha256(d.encode()).hexdigest()[:12]}.json'
parent = lambda p: p.rsplit('/', 1)[0] if '/' in p else ''; name = lambda p: p.rsplit('/', 1)[-1]
folders = defaultdict(lambda: dict(dirs=[], files={}))
for d in head['dirs']:
    if d: folders[parent(d)]['dirs'].append(name(d))
for p, e in head['flat'].items(): folders[parent(p)]['files'][name(p)] = dict(blob=e['blob_id'], size=e['size'])
snapshot = {key(d): pj(dict(path=d, **f)) for d, f in folders.items()}
rnd = random.Random(5); files = list(head['flat']); cur = {}
def member(k):
    if k not in cur: cur[k] = uj(snapshot[k])
    return cur[k]
deltas = []; t = time.perf_counter()
for c in range(1000):
    cid = f'c{c:05d}'; changes = []; touched = set()
    for p in rnd.sample(files, 5):
        nb = 'obj-cas-imm-' + hashlib.sha256(f'{p}{c}'.encode()).hexdigest()[:12]
        f = member(key(parent(p))); old = f['files'][name(p)]['blob']; f['files'][name(p)]['blob'] = nb
        changes.append([p, old, nb]); touched.add(key(parent(p))); d = parent(p)
        while d:
            d = parent(d); member(key(d))['rev'] = cid; touched.add(key(d))
    m = {k: pj(cur[k]) for k in touched}; m['changes.json'] = pj(dict(commit=cid, changes=changes))
    deltas.append(m)
R = dict(writer_1000_commits_s=round(time.perf_counter() - t, 2))
sz = sorted(sum(map(len, d.values())) for d in deltas); ch = sorted(len(d['changes.json']) for d in deltas)
R['delta_members_median'] = sorted(len(d) for d in deltas)[500]; R['delta_kb_median'] = round(sz[500] / 1e3, 1)
R['changes_record_bytes_median'] = ch[500]; R['deltas_total_mb'] = round(sum(sz) / 1e6, 2)
R['snapshot_mb'] = round(sum(map(len, snapshot.values())) / 1e6, 2)
# the reader: blob -> paths and file -> commits from the snapshot once, then the 1,000 change records applied
t = time.perf_counter(); bp = defaultdict(set)
for p, e in head['flat'].items(): bp[e['blob_id']].add(p)
R['xref_from_snapshot_ms'] = round((time.perf_counter() - t) * 1e3, 1)
t = time.perf_counter(); fc = defaultdict(list)
for d in deltas:
    rec = uj(d['changes.json'])
    for p, old, nb in rec['changes']:
        bp[old].discard(p); bp[nb].add(p); fc[p].append(rec['commit'])
R['apply_1000_change_records_ms'] = round((time.perf_counter() - t) * 1e3, 1)
print(json.dumps(R, indent=1)); json.dump(R, open(f'{S}/dl/deltas_lean.json', 'w'), indent=1)
