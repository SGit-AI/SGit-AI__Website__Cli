# The reader alone, in a fresh process: the zip mapped (mmap), not read; the offset table first; shards on demand.
import json, zlib, mmap, struct, time, os, sys, random, resource
S = os.environ['S']; N = int(sys.argv[1]); SH = int(sys.argv[2]); path = f'{S}/wk/wiki_{N}.zip'
rss = lambda: round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
R = dict(pages=N, rss_at_start_mb=rss())
t = time.perf_counter()
f = open(path, 'rb'); mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
n, e = struct.unpack('<HH', mm[26:30]); cs = struct.unpack('<I', mm[18:22])[0]
OFFS = json.loads(zlib.decompressobj().decompress(mm[30+n+e:30+n+e+cs]))
R['open_ms'] = round((time.perf_counter()-t)*1e3, 1); R['rss_after_open_mb'] = rss()
cache = {}; loads = [0]
def get(k):
    if k not in cache:
        o, l = OFFS[k]; cache[k] = json.loads(zlib.decompress(mm[o:o+l])); loads[0] += 1
    return cache[k]
OUTL = lambda i: get(f'out/{i % SH:05d}.json')[str(i)]
BACK = lambda i: get(f'back/{i % SH:05d}.json')[str(i)]
def shortest(a, b):
    fa, fb = {a: 0}, {b: 0}; qa, qb = [a], [b]
    while qa and qb:
        if len(qa) <= len(qb):
            nq = []
            for x in qa:
                for y in OUTL(x):
                    if y in fb: return fa[x] + 1 + fb[y]
                    if y not in fa: fa[y] = fa[x] + 1; nq.append(y)
            qa = nq
        else:
            nq = []
            for x in qb:
                for y in BACK(x):
                    if y in fa: return fb[x] + 1 + fa[y]
                    if y not in fb: fb[y] = fb[x] + 1; nq.append(y)
            qb = nq
rnd = random.Random(29); paths = []
for k in range(10):
    a, b = rnd.randrange(N // 2, N), rnd.randrange(N // 2, N)
    cache.clear(); loads[0] = 0; t = time.perf_counter(); d = shortest(a, b)
    paths.append(dict(ms=round((time.perf_counter()-t)*1e3, 1), shards=loads[0], hops=d))
R['shortest_paths_cold'] = paths
ms = sorted(p['ms'] for p in paths); sh = sorted(p['shards'] for p in paths)
R['shortest_ms_median'] = ms[5]; R['shortest_ms_max'] = ms[-1]; R['shards_median'] = sh[5]; R['shards_max'] = sh[-1]
R['max_rss_mb'] = rss()
print(json.dumps(R)); json.dump(R, open(f'{S}/wk/wiki_reader_{N}.json', 'w'), indent=1)
