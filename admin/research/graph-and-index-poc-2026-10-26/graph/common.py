import json, time, os, sys
S = os.environ['S']; GX = f'{S}/gx'
T = json.load(open(f'{GX}/triples.json')); M = json.load(open(f'{GX}/meta.json'))
QUERIES = ['children', 'subtree_files', 'file_to_root', 'ancestors_of_head', 'merge_base', 'base_to_head', 'file_history', 'paths_of_blob']
def timed(fn, n=None):
    t = time.perf_counter(); r = fn(); first = time.perf_counter() - t
    if n is None: n = 1 if first > 0.5 else (5 if first > 0.05 else 50)
    t = time.perf_counter()
    for _ in range(n): r = fn()
    sec = (time.perf_counter() - t) / n
    print(f'    .. {sec*1e3:.3f} ms', flush=True)
    return r, sec
def report(engine, load_s, size, results, extra=''):
    truth = json.load(open(f'{GX}/truth.json')) if os.path.exists(f'{GX}/truth.json') else None
    out = dict(engine=engine, load_s=round(load_s, 2), size_mb=round(size / 1e6, 1) if size else None, q={}, extra=extra)
    for q, (val, sec) in results.items():
        ok = '' if truth is None else ('ok' if truth[q] == val else f'MISMATCH {val} != {truth[q]}')
        out['q'][q] = dict(ms=round(sec * 1e3, 3), val=val, ok=ok)
        print(f'  {q:18s} {sec*1e3:10.3f} ms  {str(val)[:40]:40s} {ok}')
    print(f'{engine}: load {load_s:.2f} s, size {size/1e6 if size else 0:.1f} MB {extra}')
    with open(f'{GX}/results.jsonl', 'a') as f: f.write(json.dumps(out) + '\n')
