# A Wikipedia-sized link graph, synthetic: N pages, each with 5 to 45 links (25 on average), targets skewed towards a
# few popular pages as real links are. The writer builds sharded JSON cross-references (outlinks, backlinks, titles) in
# one zip with an offset table; the reader answers lookups and shortest paths loading shards on demand. Compared with
# loading the whole graph into memory as compact arrays (CSR, stdlib array).
import json, zlib, zipfile, time, os, sys, random, array, resource, struct, gc
from collections import defaultdict, deque
S = os.environ['S']; N = int(sys.argv[1]); SH = int(sys.argv[2]); OUT = f'{S}/wk/wiki_{N}.zip'
rss = lambda: round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
rnd = random.Random(11); R = dict(pages=N, shards=SH)
t = time.perf_counter()
out = [None] * N
for i in range(N):
    k = rnd.randint(5, 45)
    out[i] = sorted({int(N * rnd.random() ** 2.5) for _ in range(k)} - {i})
E = sum(len(x) for x in out); R['links'] = E; R['generate_s'] = round(time.perf_counter() - t, 1)
title = lambda i: f'Page_{i:07d}_{"abcdefghij"[i % 10]}'
# the writer
t = time.perf_counter()
back = [[] for _ in range(N)]
for i, xs in enumerate(out):
    for j in xs: back[j].append(i)
R['writer_backlinks_s'] = round(time.perf_counter() - t, 1)
t = time.perf_counter()
pj = lambda o: zlib.compress(json.dumps(o, separators=(',', ':')).encode(), 6)
members = {}
for s in range(SH):
    ids = range(s, N, SH)
    members[f'out/{s:05d}.json'] = pj({str(i): out[i] for i in ids})
    members[f'back/{s:05d}.json'] = pj({str(i): back[i] for i in ids})
    members[f'title/{s:05d}.json'] = pj({str(i): title(i) for i in ids})
tid = defaultdict(dict)
for i in range(N): tid[zlib.crc32(title(i).encode()) % SH][title(i)] = i
for s, d in tid.items(): members[f'by-title/{s:05d}.json'] = pj(d)
R['writer_shards_s'] = round(time.perf_counter() - t, 1)
names = sorted(members); OFF = 'offsets.json'
def layout(res):
    pos = 30 + len(OFF) + res; o = {}
    for nm in names: o[nm] = [pos + 30 + len(nm), len(members[nm])]; pos += 30 + len(nm) + len(members[nm])
    return o
reserved = len(zlib.compress(json.dumps(layout(10**10)).encode(), 6)) + 4096
offs = layout(reserved); packed = zlib.compress(json.dumps(offs).encode(), 6)
t = time.perf_counter()
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_STORED, allowZip64=True) as z:
    z.writestr(zipfile.ZipInfo(OFF, (1980, 1, 1, 0, 0, 0)), packed + b'\0' * (reserved - len(packed)))
    for nm in names: z.writestr(zipfile.ZipInfo(nm, (1980, 1, 1, 0, 0, 0)), members[nm])
R['writer_zip_s'] = round(time.perf_counter() - t, 1); R['zip_mb'] = round(os.path.getsize(OUT) / 1e6, 1); R['members'] = len(members) + 1
for g in ('out', 'back', 'title', 'by-title'):
    sz = [len(v) for k, v in members.items() if k.startswith(g + '/')]; R[f'{g}_mb'] = round(sum(sz) / 1e6, 1); R[f'{g}_shard_median_kb'] = round(sorted(sz)[len(sz)//2] / 1e3, 1)
# compact arrays for the in-memory comparison: offsets + targets, int32
t = time.perf_counter()
o_idx = array.array('q', [0]); o_tgt = array.array('i')
for xs in out: o_tgt.extend(xs); o_idx.append(len(o_tgt))
b_idx = array.array('q', [0]); b_tgt = array.array('i')
for xs in back: b_tgt.extend(xs); b_idx.append(len(b_tgt))
csr = o_idx.tobytes() + o_tgt.tobytes() + b_idx.tobytes() + b_tgt.tobytes()
R['csr_build_s'] = round(time.perf_counter() - t, 1); R['csr_mb'] = round(len(csr) / 1e6, 1); R['csr_deflated_mb'] = round(len(zlib.compress(csr, 1)) / 1e6, 1)
del members; gc.collect()
# the reader: offsets first, shards on demand
data = open(OUT, 'rb').read(); mv = memoryview(data)
t = time.perf_counter()
h = data[:30]; n, e = struct.unpack('<HH', h[26:30]); cs = struct.unpack('<I', h[18:22])[0]
OFFS = json.loads(zlib.decompressobj().decompress(data[30+n+e:30+n+e+cs])); R['reader_open_ms'] = round((time.perf_counter()-t)*1e3, 1)
cache = {}; loads = [0]
def get(k):
    if k not in cache:
        o, l = OFFS[k]; cache[k] = json.loads(zlib.decompress(mv[o:o+l])); loads[0] += 1
    return cache[k]
OUTL = lambda i: get(f'out/{i % SH:05d}.json')[str(i)]
BACK = lambda i: get(f'back/{i % SH:05d}.json')[str(i)]
def shortest(a, b, nb_f, nb_b):
    if a == b: return 0
    fa, fb = {a: 0}, {b: 0}; qa, qb = [a], [b]; d = 0
    while qa and qb:
        if len(qa) <= len(qb):
            nq = []
            for x in qa:
                for y in nb_f(x):
                    if y in fb: return fa[x] + 1 + fb[y]
                    if y not in fa: fa[y] = fa[x] + 1; nq.append(y)
            qa = nq
        else:
            nq = []
            for x in qb:
                for y in nb_b(x):
                    if y in fa: return fb[x] + 1 + fa[y]
                    if y not in fb: fb[y] = fb[x] + 1; nq.append(y)
            qb = nq
    return None
pairs = [(rnd.randrange(N // 2, N), rnd.randrange(N // 2, N)) for _ in range(5)]          # unpopular pages: the hard case
def q(label, fn):
    cache.clear(); loads[0] = 0; t = time.perf_counter(); v = fn(); R[label] = dict(ms=round((time.perf_counter()-t)*1e3, 1), shards=loads[0], answer=v)
q('outlinks of a page', lambda: len(OUTL(pairs[0][0])))
q('backlinks of a popular page', lambda: len(BACK(3)))
q('title to id to outlinks', lambda: len(OUTL(get(f'by-title/{zlib.crc32(title(777).encode()) % SH:05d}.json')[title(777)])))
q('pages two links away', lambda: len({y for x in OUTL(pairs[0][0]) for y in OUTL(x)}))
for k, (a, b) in enumerate(pairs[:3]): q(f'shortest path {k+1}, on demand', lambda a=a, b=b: shortest(a, b, OUTL, BACK))
R['reader_max_rss_mb_on_demand'] = rss()
# whole graph in memory from the compact arrays
t = time.perf_counter()
oi = array.array('q'); oi.frombytes(o_idx.tobytes()); ot = array.array('i'); ot.frombytes(o_tgt.tobytes())
bi = array.array('q'); bi.frombytes(b_idx.tobytes()); bt = array.array('i'); bt.frombytes(b_tgt.tobytes())
R['csr_load_ms'] = round((time.perf_counter()-t)*1e3, 1)
NF = lambda x: ot[oi[x]:oi[x+1]]; NB = lambda x: bt[bi[x]:bi[x+1]]
for k, (a, b) in enumerate(pairs[:3]):
    t = time.perf_counter(); v = shortest(a, b, NF, NB); R[f'shortest path {k+1}, arrays in memory'] = dict(ms=round((time.perf_counter()-t)*1e3, 1), answer=v)
R['max_rss_mb'] = rss()
print(json.dumps(R, indent=1)); json.dump(R, open(f'{S}/wk/wiki_{N}.json', 'w'), indent=1)
