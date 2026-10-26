# Builds the graph dataset as triples (s, p, o) from the 76,000-file head and a synthetic commit DAG.
import json, random, sys, hashlib, os
S = sys.argv[1]; OUT = f'{S}/gx'
head = json.load(open(f'{S}/bench/v/.sg_vault/local/flat-cache/obj-cas-imm-7473af178535.json'))
rnd = random.Random(7)
T = []                                                    # triples
def parent_of(p): return p.rsplit('/', 1)[0] if '/' in p else ''
for d in head['dirs']:                                    # folders: path nodes
    if d: T.append((f'd:{parent_of(d)}', 'contains', f'd:{d}'))
    T.append((f'd:{d}', 'tree', head['dirs'][d]))
for p, e in head['flat'].items():
    T.append((f'd:{parent_of(p)}', 'contains', f'f:{p}'))
    T.append((f'f:{p}', 'blob', e['blob_id']))
    T.append((f'f:{p}', 'size', str(e['size'])))
files = list(head['flat'])
# commit DAG: a main line; every 50 commits a side branch of 5 merged back; one unmerged side branch at the end
N = 20000; commits = []; main = None; ts = 1_760_000_000; meta = {}
def cid(i): return 'c' + hashlib.sha256(str(i).encode()).hexdigest()[:12]
i = 0
while i < N:
    c = cid(i); i += 1; ts += 60
    if main: T.append((c, 'parent', main))
    T.append((c, 'ts', str(ts)))
    for p in rnd.sample(files, 5): T.append((c, 'changed', f'f:{p}'))
    main = c; commits.append(c)
    if i % 50 == 0 and i < N - 10:
        side = main
        for _ in range(5):
            s = cid(i); i += 1; ts += 60
            T.append((s, 'parent', side)); T.append((s, 'ts', str(ts)))
            for p in rnd.sample(files, 5): T.append((s, 'changed', f'f:{p}'))
            side = s
        m = cid(i); i += 1; ts += 60
        T.append((m, 'parent', main)); T.append((m, 'parent', side)); T.append((m, 'ts', str(ts)))
        main = m
fork = cid(i - 120)                                       # an unmerged branch from 120 back
side = fork
for k in range(3):
    s = 'cside' + str(k); T.append((s, 'parent', side)); T.append((s, 'ts', str(ts + k))); side = s
meta = dict(head=main, side_tip=side, fork=fork, base=None, file=files[123], folder='raw/c09', folder_deep='raw/c09/s4',
            blob=head['flat'][files[123]]['blob_id'])
# base for base..head: the main head 100 first-parent steps back
par = {}
for s, p, o in T:
    if p == 'parent': par.setdefault(s, []).append(o)
b = main
for _ in range(100): b = par[b][0]
meta['base'] = b
json.dump(T, open(f'{OUT}/triples.json', 'w')); json.dump(meta, open(f'{OUT}/meta.json', 'w'))
from collections import Counter
print(len(T), 'triples', dict(Counter(p for _, p, _ in T)), 'commits', sum(1 for s,p,o in T if p=='ts'))
print(meta)
