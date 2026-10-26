# Every commit pack carries the index changes of its commit (a delta); a snapshot carries the whole index.
# 1,000 commits of 5 files each on the 76,000-file vault: delta sizes, the reader's two ways to assemble them
# (an overlay that finds the newest version of a member, or one local merge), compaction, and history from the deltas.
import json, zlib, time, os, hashlib, random
from collections import defaultdict
S = os.environ['S']; head = json.load(open(f'{S}/bench/v/.sg_vault/local/flat-cache/obj-cas-imm-7473af178535.json'))
pj = lambda o: zlib.compress(json.dumps(o, separators=(',', ':'), sort_keys=True).encode(), 6)
uj = lambda b: json.loads(zlib.decompress(b))
key = lambda d: f'folders/{hashlib.sha256(d.encode()).hexdigest()[:12]}.json'
xkey = lambda kind, k: f'xref/{kind}/{hashlib.sha256(k.encode()).hexdigest()[:2]}.json'
parent = lambda p: p.rsplit('/', 1)[0] if '/' in p else ''; name = lambda p: p.rsplit('/', 1)[-1]
# the snapshot index, as members (folder files with subtree totals; blob -> paths; file -> commits)
folders = defaultdict(lambda: dict(dirs=[], files={}))
for d in head['dirs']:
    if d: folders[parent(d)]['dirs'].append(name(d))
for p, e in head['flat'].items(): folders[parent(p)]['files'][name(p)] = dict(blob=e['blob_id'], size=e['size'])
for d in sorted(folders, key=lambda x: -(x.count('/') + (1 if x else 0))):
    f = folders[d]; f['n'] = len(f['files']) + sum(folders[f'{d}/{s}' if d else s]['n'] for s in f['dirs'])
bp = defaultdict(dict)
for p, e in head['flat'].items(): bp[xkey('blob-paths', e['blob_id'])].setdefault(e['blob_id'], []).append(p)
t = time.perf_counter()
snapshot = {key(d): pj(dict(path=d, **f)) for d, f in folders.items()}
snapshot.update({k: pj(v) for k, v in bp.items()})
R = dict(snapshot_members=len(snapshot), snapshot_mb=round(sum(map(len, snapshot.values())) / 1e6, 2), snapshot_build_s=round(time.perf_counter() - t, 2))
# 1,000 commits: the writer emits only what each commit changes
rnd = random.Random(5); files = list(head['flat']); cur = {}            # cur: the writer's working copy of changed members
def member(k):
    if k not in cur: cur[k] = uj(snapshot[k]) if k in snapshot else {}
    return cur[k]
deltas = []; t = time.perf_counter()
for c in range(1000):
    cid = f'c{c:05d}'; changed = rnd.sample(files, 5); touched = set()
    for p in changed:
        nb = hashlib.sha256(f'{p}{c}'.encode()).hexdigest()[:12]
        f = member(key(parent(p))); old = f['files'][name(p)]['blob']; f['files'][name(p)] = dict(blob=f'obj-cas-imm-{nb}', size=f['files'][name(p)]['size'])
        touched.add(key(parent(p)))
        d = parent(p)
        while d:                                                       # the parents' files change with their children's ids
            d = parent(d); member(key(d))['rev'] = cid; touched.add(key(d))
        ob = member(xkey('blob-paths', old)); ob[old] = [x for x in ob.get(old, []) if x != p]
        if not ob[old]: del ob[old]
        nbm = member(xkey('blob-paths', f'obj-cas-imm-{nb}')); nbm.setdefault(f'obj-cas-imm-{nb}', []).append(p)
        fc = member(xkey('file-commits', p)); fc.setdefault(p, []).append(cid)
        touched |= {xkey('blob-paths', old), xkey('blob-paths', f'obj-cas-imm-{nb}'), xkey('file-commits', p)}
    deltas.append(dict(commit=cid, changed=changed, members={k: pj(cur[k]) for k in touched}))
R['writer_1000_commits_s'] = round(time.perf_counter() - t, 2)
sz = sorted(sum(map(len, d['members'].values())) for d in deltas); nm = sorted(len(d['members']) for d in deltas)
R['delta_members_median'] = nm[500]; R['delta_kb_median'] = round(sz[500] / 1e3, 1); R['deltas_total_mb'] = round(sum(sz) / 1e6, 2)
# reader A: an overlay. Newest delta wins; a map from member name to the newest pack holding it, built once.
t = time.perf_counter(); newest = {}
for i, d in enumerate(deltas):
    for k in d['members']: newest[k] = i
R['overlay_map_build_ms'] = round((time.perf_counter() - t) * 1e3, 1); R['overlay_map_entries'] = len(newest)
def read(k): return uj(deltas[newest[k]]['members'][k]) if k in newest else uj(snapshot[k]) if k in snapshot else {}
probe = rnd.sample(list(snapshot), 2000); t = time.perf_counter()
for k in probe: read(k)
R['overlay_read_us'] = round((time.perf_counter() - t) / len(probe) * 1e6, 1)
# check: the overlay gives the writer's final state
assert all(read(k) == v for k, v in cur.items())
# reader B: merge once into a local copy (what compaction does on the host, done locally)
t = time.perf_counter(); merged = dict(snapshot)
for d in deltas: merged.update(d['members'])
R['local_merge_ms'] = round((time.perf_counter() - t) * 1e3, 1)
# change over time, from the deltas alone: the versions of one folder, and every commit that touched a subtree
p0 = deltas[0]['changed'][0]; d0 = parent(p0)
t = time.perf_counter(); versions = [d['commit'] for d in deltas if key(d0) in d['members']]
R['folder_versions_ms'] = round((time.perf_counter() - t) * 1e3, 2); R['folder_versions'] = len(versions)
sub = 'raw/c03/'; t = time.perf_counter(); hits = [d['commit'] for d in deltas if any(x.startswith(sub) for x in d['changed'])]
R['commits_touching_raw_c03_ms'] = round((time.perf_counter() - t) * 1e3, 2); R['commits_touching_raw_c03'] = len(hits)
print(json.dumps(R, indent=1)); json.dump(R, open(f'{S}/dl/deltas.json', 'w'), indent=1)
