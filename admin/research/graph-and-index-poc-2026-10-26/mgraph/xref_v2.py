# Two writer-side fixes: commits sharded by generation range (a walk stays in one or two shards), and an offset table
# written as the zip's first member, so a reader never parses the zip's 58,831-entry central directory.
import json, zlib, zipfile, time, os, io, struct, heapq
from collections import defaultdict
S = os.environ['S']; GX = f'{S}/gx'; T = json.load(open(f'{GX}/triples.json')); M = json.load(open(f'{GX}/meta.json'))
src = zipfile.ZipFile(f'{S}/mg/xref.zip'); members = {zi.filename: src.read(zi) for zi in src.infolist() if not zi.filename.startswith('xref/commits/')}
pj = lambda o: zlib.compress(json.dumps(o, separators=(',', ':'), sort_keys=True).encode(), 6)
par = defaultdict(list); ts = {}; changed = defaultdict(list)
for s, p, o in T:
    if p == 'parent': par[s].append(o)
    elif p == 'ts': ts[s] = int(o)
    elif p == 'changed': changed[s].append(o[2:])
gen = {}
for c in sorted(ts, key=ts.get): gen[c] = 1 + max((gen[x] for x in par[c]), default=0)
G = 1000
by = defaultdict(dict)
for c in ts: by[gen[c] // G][c] = dict(parents=par[c], gen=gen[c], ts=ts[c], changed=changed[c])
for k, v in by.items(): members[f'xref/commits-by-gen/{k:05d}.json'] = pj(v)
members['xref/commit-gen.json'] = pj(gen)                                         # commit id -> generation: which shard to open
# lay out: a fixed-size header member first, holding the offsets of every other member
names = sorted(members); body = io.BytesIO(); offsets = {}
OFF = 'offsets.json'
def local(nm, data):
    zi = zipfile.ZipInfo(nm, (1980, 1, 1, 0, 0, 0)); return zi
t = time.perf_counter()
# pass 1: compute offsets assuming the offsets member comes first with a known length; iterate to a fixed point
def layout(reserved):
    pos = 30 + len(OFF) + reserved; o = {}
    for nm in names:
        o[nm] = [pos + 30 + len(nm.encode()), len(members[nm])]; pos += 30 + len(nm.encode()) + len(members[nm])
    return o
probe = zlib.compress(json.dumps(layout(10**8), separators=(',', ':')).encode(), 6)
reserved = len(probe) + 4096                                                     # a fixed size the table is padded to
offsets = layout(reserved)
packed = zlib.compress(json.dumps(offsets, separators=(',', ':')).encode(), 6)
assert len(packed) <= reserved
blob = packed + b'\0' * (reserved - len(packed))
out = f'{S}/mg/xref_v2.zip'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as z:
    z.writestr(zipfile.ZipInfo(OFF, (1980, 1, 1, 0, 0, 0)), blob)
    for nm in names: z.writestr(zipfile.ZipInfo(nm, (1980, 1, 1, 0, 0, 0)), members[nm])
tw = time.perf_counter() - t
chk = zipfile.ZipFile(out)
for zi in chk.infolist()[1:]:
    assert offsets[zi.filename][0] == zi.header_offset + 30 + len(zi.filename.encode()), zi.filename
# reader: read the first local header, then the offsets member, never the central directory
t = time.perf_counter()
with open(out, 'rb') as f:
    h = f.read(30); n, e = struct.unpack('<HH', h[26:30]); csize = struct.unpack('<I', h[18:22])[0]
    f.seek(30 + n + e); offs = json.loads(zlib.decompressobj().decompress(f.read(csize)))
topen = time.perf_counter() - t
data = open(out, 'rb').read(); mv = memoryview(data); cache = {}; loads = [0]
def get(k):
    if k not in cache:
        o, l = offs[k]; cache[k] = json.loads(zlib.decompress(mv[o:o+l])); loads[0] += 1
    return cache[k]
cg = None
def C(c):
    return get(f'xref/commits-by-gen/{get("xref/commit-gen.json")[c] // G:05d}.json')[c]
def paint(a, b):
    flags = defaultdict(int); flags[a] |= 1; flags[b] |= 2; qq = [(-C(a)['gen'], a), (-C(b)['gen'], b)]; seen = {a, b}
    while qq and any(flags[c] != 3 for _, c in qq):
        _, c = heapq.heappop(qq)
        for p in C(c)['parents']:
            flags[p] |= flags[c]
            if p not in seen: seen.add(p); heapq.heappush(qq, (-C(p)['gen'], p))
    return flags
R = dict(writer_layout_s=round(tw, 2), zip_mb=round(os.path.getsize(out)/1e6, 2), offsets_member_kb=round(len(blob)/1e3, 1),
         reader_open_without_central_directory_ms=round(topen*1e3, 1))
for label, fn in [('merge base', lambda: max((c for c, v in paint(M['head'], M['side_tip']).items() if v == 3), key=lambda c: C(c)['gen'])),
                  ('base..head', lambda: sum(1 for v in paint(M['head'], M['base']).values() if v == 1))]:
    cache.clear(); loads[0] = 0; t = time.perf_counter(); v = fn()
    R[label] = dict(ms=round((time.perf_counter()-t)*1e3, 2), members_loaded=loads[0], answer=v)
print(json.dumps(R, indent=1)); json.dump(R, open(f'{S}/mg/xref_v2.json', 'w'), indent=1)
