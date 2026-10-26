# The writer-pays, JSON-native index of the vault: one JSON per folder (its entries plus subtree totals), and cross-reference
# shards (blob -> paths, file -> commits that changed it, commit -> parents/generation/ts/changed), each member deflated JSON in
# one zip. Then: the writer's incremental cost for one commit, and the reader's queries loading members on demand.
import json, zlib, zipfile, time, os, hashlib, io, random
from collections import defaultdict
S = os.environ['S']; GX = f'{S}/gx'; OUT = f'{S}/mg/xref.zip'
head = json.load(open(f'{S}/bench/v/.sg_vault/local/flat-cache/obj-cas-imm-7473af178535.json'))
T = json.load(open(f'{GX}/triples.json')); M = json.load(open(f'{GX}/meta.json'))
pj = lambda o: zlib.compress(json.dumps(o, separators=(',', ':'), sort_keys=True).encode(), 6)
shard = lambda key, n: hashlib.sha256(key.encode()).hexdigest()[:n]
parent = lambda p: p.rsplit('/', 1)[0] if '/' in p else ''
name = lambda p: p.rsplit('/', 1)[-1]
t0 = time.perf_counter()
# 1. folders: entries, and totals over the subtree
folders = defaultdict(lambda: dict(dirs={}, files={}))
for d, tid in head['dirs'].items():
    folders[d]['tree'] = tid
    if d: folders[parent(d)]['dirs'][name(d)] = tid
for p, e in head['flat'].items():
    folders[parent(p)]['files'][name(p)] = dict(blob=e['blob_id'], size=e['size'], hash=e['content_hash'], type=e['content_type'])
for d in sorted(folders, key=lambda x: -x.count('/') - (1 if x else 0)):                  # deepest first: totals roll up
    f = folders[d]; n = len(f['files']); b = sum(x['size'] for x in f['files'].values())
    for sub in f['dirs']:
        c = folders[f'{d}/{sub}' if d else sub]; n += c['n_files']; b += c['bytes']
    f['n_files'] = n; f['bytes'] = b
# 2. cross references
blob_paths = defaultdict(lambda: defaultdict(list)); file_commits = defaultdict(lambda: defaultdict(list))
par = defaultdict(list); ts = {}; changed = defaultdict(list)
for s, p, o in T:
    if p == 'parent': par[s].append(o)
    elif p == 'ts': ts[s] = int(o)
    elif p == 'changed': changed[s].append(o[2:])
for p, e in head['flat'].items(): blob_paths[shard(e['blob_id'], 2)][e['blob_id']].append(p)
for c, fs in changed.items():
    for f in fs: file_commits[shard(f, 2)][f].append(c)
gen = {}
for c in sorted(ts, key=ts.get): gen[c] = 1 + max((gen[x] for x in par[c]), default=0)
commit_shards = defaultdict(dict)
for c in ts: commit_shards[shard(c, 2)][c] = dict(parents=par[c], gen=gen[c], ts=ts[c], changed=changed[c])
members = {}
for d, f in folders.items(): members[f'folders/{shard(d, 12)}.json'] = pj(dict(path=d, **f))
for k, v in blob_paths.items(): members[f'xref/blob-paths/{k}.json'] = pj(v)
for k, v in file_commits.items(): members[f'xref/file-commits/{k}.json'] = pj(v)
for k, v in commit_shards.items(): members[f'xref/commits/{k}.json'] = pj(v)
members['heads.json'] = pj(dict(head=M['head'], root=head['dirs']['']))
build = time.perf_counter() - t0
t = time.perf_counter()
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_STORED) as z:
    for k in sorted(members):
        zi = zipfile.ZipInfo(k, (1980, 1, 1, 0, 0, 0)); z.writestr(zi, members[k])
tw = time.perf_counter() - t
groups = defaultdict(lambda: [0, 0])
for k, v in members.items(): g = k.rsplit('/', 1)[0]; groups[g][0] += 1; groups[g][1] += len(v)
R = dict(writer_full_build_s=round(build, 2), writer_zip_s=round(tw, 2), zip_mb=round(os.path.getsize(OUT)/1e6, 2), members=len(members),
         groups={g: dict(members=n, mb=round(b/1e6, 2), median_bytes=sorted(len(v) for k, v in members.items() if k.rsplit('/', 1)[0] == g)[n // 2]) for g, (n, b) in groups.items()})
# 3. the writer's incremental cost for one commit that changes 5 files: the folders on their paths, and the shards they touch
rnd = random.Random(3); files = rnd.sample(list(head['flat']), 5)
t = time.perf_counter(); touched = set()
for p in files:
    d = parent(p)
    while True:
        touched.add(f'folders/{shard(d, 12)}.json')
        if d == '': break
        d = parent(d)
    touched.add(f'xref/blob-paths/{shard(head["flat"][p]["blob_id"], 2)}.json'); touched.add(f'xref/file-commits/{shard(p, 2)}.json')
touched.add(f'xref/commits/{shard("cnew", 2)}.json')
rewrite = {k: pj(json.loads(zlib.decompress(members[k]))) for k in touched}                # decode, change, encode again
R['writer_one_commit'] = dict(files=5, members_rewritten=len(rewrite), bytes=sum(len(v) for v in rewrite.values()),
                              ms=round((time.perf_counter() - t) * 1e3, 1), folder_members=sum(1 for k in touched if k.startswith('folders/')))
# 4. the reader: open the zip once (offset index), load members on demand, cache them
t = time.perf_counter(); data = open(OUT, 'rb').read(); zf = zipfile.ZipFile(io.BytesIO(data))
off = {zi.filename: (zi.header_offset + 30 + len(zi.filename.encode()), zi.compress_size) for zi in zf.infolist()}
topen = time.perf_counter() - t
mv = memoryview(data); cache = {}; loads = [0]
def get(k):
    if k not in cache:
        o, l = off[k]; cache[k] = json.loads(zlib.decompress(mv[o:o+l])); loads[0] += 1
    return cache[k]
folder = lambda d: get(f'folders/{shard(d, 12)}.json')
def q(label, fn, cold=True):
    if cold: cache.clear()
    loads[0] = 0; t = time.perf_counter(); v = fn(); ms = (time.perf_counter() - t) * 1e3
    R.setdefault('reader', {})[label] = dict(ms=round(ms, 3), members_loaded=loads[0], answer=v); return v
f1 = M['file']
q('list a folder', lambda: len(folder(M['folder_deep'])['files']) + len(folder(M['folder_deep'])['dirs']))
q('files and bytes under raw/c09 (rolled-up totals)', lambda: [folder(M['folder'])['n_files'], folder(M['folder'])['bytes']])
q('does a file exist, and its blob (one folder)', lambda: folder(parent(f1))['files'][name(f1)]['blob'])
def walk(d):
    f = folder(d); n = len(f['files'])
    for sub in f['dirs']: n += walk(f'{d}/{sub}')
    return n
q('every file under raw/c09/s4, walked', lambda: walk(M['folder_deep']))
q('paths that hold a blob', lambda: get(f'xref/blob-paths/{shard(M["blob"], 2)}.json')[M['blob']])
q('commits that changed a file', lambda: len(get(f'xref/file-commits/{shard(f1, 2)}.json').get(f1, [])))
C = lambda c: get(f'xref/commits/{shard(c, 2)}.json')[c]
import heapq
def paint(a, b):
    flags = defaultdict(int); flags[a] |= 1; flags[b] |= 2; qq = [(-C(a)['gen'], a), (-C(b)['gen'], b)]; seen = {a, b}
    while qq and any(flags[c] != 3 for _, c in qq):
        _, c = heapq.heappop(qq)
        for p in C(c)['parents']:
            flags[p] |= flags[c]
            if p not in seen: seen.add(p); heapq.heappush(qq, (-C(p)['gen'], p))
    return flags
q('merge base (generation walk, shards on demand)', lambda: max((c for c, v in paint(M['head'], M['side_tip']).items() if v == 3), key=lambda c: C(c)['gen']))
q('base..head (generation walk, shards on demand)', lambda: sum(1 for v in paint(M['head'], M['base']).values() if v == 1))
q('merge base again, shards cached', lambda: max((c for c, v in paint(M['head'], M['side_tip']).items() if v == 3), key=lambda c: C(c)['gen']), cold=False)
R['reader_open_ms'] = round(topen * 1e3, 1)
print(json.dumps(R, indent=1)); json.dump(R, open(f'{S}/mg/xref_index.json', 'w'), indent=1)
